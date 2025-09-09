#Guardamos las funciones que se usan en el backend de la aplicación para la gestión de alumnos y asignaturas.

# Añadimos todas las librerias necesarias
import hashlib
from fastapi import File, HTTPException
import oracledb as oracledb
import pandas as pd
import pdfplumber
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Funciones sobre la vista para probabilidades y machine learning

def calcular_media_ponderada_vista(cur: oracledb.Cursor, codigo_alumno, curso_max):
    cur.execute("""
        SELECT 
            AVG(TO_NUMBER(NUM_CALIFICACIÓN)) AS media_aprobadas,
            COUNT(*) AS asignaturas_aprobadas,
            SUM(CREDITOS) AS creditos_aprobados
        FROM v_calificaciones
        WHERE CODIGOALUM = :codigo
        AND CALIFICACIÓN NOT IN ('NO PRESENTADO', 'SUSPENSO')
        AND TO_NUMBER(SUBSTR(CURSOACADÉMICO, 1, 4)) < TO_NUMBER(SUBSTR(:curso_inicio , 1, 4))
    """, codigo=codigo_alumno, curso_inicio=curso_max[:4])
    resultado = cur.fetchone() #Como esperamos solo un resultado, uso fetchone
    media, aprobadas, creditos = resultado
    if media is None or aprobadas == 0:
        return (None, 0)  # Evitamos división por cero o falta de datos
    ponderada = (media * creditos) / 240
    return (round(ponderada, 2), aprobadas) #CAMBIO: Devuelvo también la cantidad de aprobadas
    
def obtener_alumnos_matriculados(cur, nombre_asignatura):
        cur.execute("""
            SELECT DISTINCT CODIGOALUM, CURSOACADÉMICO
            FROM v_calificaciones
            WHERE REPLACE(NOMBREASIGNATURA, ' ', '') = :asignatura
        """, asignatura=nombre_asignatura)

        return cur.fetchall()

def calcular_nota_corte(cur, nombre_asignatura):
    # 1. Obtener alumnos + curso académico donde cursaron esa asignatura
    alumnos_con_curso = obtener_alumnos_matriculados(cur, nombre_asignatura)

    # 2. Agrupar alumnos por curso académico
    cursos = {}
    for codigo_alum, curso_acad in alumnos_con_curso:
        cursos.setdefault(curso_acad, []).append(codigo_alum)

    # 3. Para cada curso, calcular la nota de corte
    nota_corte_por_año = {}

    for curso_acad, codigos_alumnos in cursos.items():
        medias = []
        for codigo_alum in codigos_alumnos:
            resultado = calcular_media_ponderada_vista(cur, codigo_alum, curso_acad)
            if resultado:
                media, aprobadas = resultado
                if media is not None and aprobadas > 10:
                    medias.append(media)
        if medias:
            nota_corte_por_año[curso_acad] = min(medias)

    return nota_corte_por_año  # Dict: { "2018-19": 6.25, "2019-20": 5.8, ... }

def calcular_probabilidad_entrada(cur, nombre_asignatura, codigo_alumno):
    media = calcular_media_ponderada_alumno(cur, codigo_alumno)[0]
    if media is None:
        raise HTTPException(status_code=400, detail=f"No se ha podido calcular la media del alumno {codigo_alumno}")
    # if media >=4:
    #     return 1
    
    # Obtener las notas de corte por año
    notas_corte = calcular_nota_corte(cur, nombre_asignatura)
    if not notas_corte or len(notas_corte) == 0:
        raise HTTPException(status_code=400, detail=f"No hay datos históricos para la asignatura {nombre_asignatura}")

    total = len(notas_corte)
    supera = 0
    
    for curso_acad, nota_corte in notas_corte.items():
        if media > nota_corte: 
            supera += 1
    
    probabilidad = (supera / total)
    return probabilidad

def crear_df(conn: oracledb.Connection):
    sql = """SELECT CODIGOALUM, REPLACE(NOMBREASIGNATURA, ' ', '') AS NOMBREASIGNATURA, NUM_CALIFICACIÓN
FROM (
    SELECT 
        CODIGOALUM,
        REPLACE(NOMBREASIGNATURA, ' ', '') AS NOMBREASIGNATURA,
        NUM_CALIFICACIÓN,
        ROW_NUMBER() OVER (
            PARTITION BY CODIGOALUM, NOMBREASIGNATURA 
            ORDER BY NUM_CALIFICACIÓN DESC
        ) AS rn
    FROM v_calificaciones
    WHERE 
        CODIGOALUM IS NOT NULL 
        OR NOMBREASIGNATURA IS NOT NULL 
        OR NUM_CALIFICACIÓN IS NOT NULL
)
WHERE rn = 1"""
    
    df = pd.read_sql(sql, conn)
    return df

def obtener_vector_alumno(
    conn: oracledb.Connection, 
    codigo_alumno: str, 
    columnas_matriz_base: list[str]
) -> pd.DataFrame:
    """
    Devuelve un DataFrame de 1 fila (index=CODIGOALUM) y columnas=columnas_matriz_base,
    con las notas del alumno alineadas a esas columnas. Rellena con 0 las que falten.
    """
    sql = """
    SELECT CODIGOALUM, REPLACE(NOMBREASIGNATURA, ' ', '') AS NOMBREASIGNATURA, NUM_CALIFICACIÓN
    FROM (
        SELECT 
            CODIGOALUM,
            REPLACE(NOMBREASIGNATURA, ' ', '') AS NOMBREASIGNATURA,
            NUM_CALIFICACIÓN,
            ROW_NUMBER() OVER (
                PARTITION BY CODIGOALUM, NOMBREASIGNATURA 
                ORDER BY NUM_CALIFICACIÓN DESC
            ) AS rn
        FROM informes_alumno
        WHERE 
            CODIGOALUM = :codigo_alumno
            AND NOMBREASIGNATURA IS NOT NULL 
            AND NUM_CALIFICACIÓN IS NOT NULL
    )
    WHERE rn = 1
    """

    df_alumno = pd.read_sql(sql, conn, params={"codigo_alumno": codigo_alumno})

    # Si no hay filas, no hay notas en informes_alumno
    if df_alumno.empty:
        return pd.DataFrame()

    # NUM_CALIFICACIÓN puede venir como '7,5' (coma). Conviértelo a float de forma robusta
    df_alumno["NUM_CALIFICACIÓN"] = (
        df_alumno["NUM_CALIFICACIÓN"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .apply(lambda x: pd.to_numeric(x, errors="coerce"))
    )

    # Pivot (1×N)
    alumno_row = df_alumno.pivot_table(
        index="CODIGOALUM",
        columns="NOMBREASIGNATURA",
        values="NUM_CALIFICACIÓN",
        aggfunc="max"
    ).fillna(0.0)

    # Alinear columnas con la matriz base (todas las asignaturas del entreno)
    alumno_row = alumno_row.reindex(columns=columnas_matriz_base, fill_value=0.0)

    return alumno_row

 
def entrenar_clustering(df:pd.DataFrame, n_clusters=12):
    # Crear matriz alumno-asignatura
    df['NUM_CALIFICACIÓN'] = pd.to_numeric(df['NUM_CALIFICACIÓN'], errors='coerce')
    matriz = df.pivot_table(index='CODIGOALUM', columns='NOMBREASIGNATURA', values='NUM_CALIFICACIÓN').fillna(0)  #Para evitar valores NaN

    scaler = StandardScaler()
    matriz_escalada = scaler.fit_transform(matriz)
    
    modelo = KMeans(n_clusters=n_clusters, random_state=42)
    modelo.fit(matriz_escalada)
    
    # Añadir etiquetas de cluster
    df_clusters = pd.DataFrame(matriz.index, columns=['CODIGOALUM'])
    df_clusters['cluster'] = modelo.labels_
    
    return modelo, scaler, matriz, df_clusters

def predecir_afinidad_cluster(
    alumno_id: str,
    asignatura: str,
    modelo: KMeans,
    scaler: StandardScaler,
    matriz_base: pd.DataFrame,
    df_clusters: pd.DataFrame,
    df_original: pd.DataFrame,
    alumno_row: pd.DataFrame | None = None,
) -> float | None:
    """
    Calcula la afinidad como combinación de:
    0.5 * nota media normalizada del cluster +
    0.5 * porcentaje de alumnos en el cluster que se matricularon en la asignatura.
    """

    asignatura_norm = str(asignatura).replace(" ", "")

    if asignatura_norm not in matriz_base.columns:
        return None

    # 1) Vector del alumno
    if alumno_row is not None:
        alumno_row = alumno_row.reindex(columns=matriz_base.columns, fill_value=0.0)
        alumno_vector_scaled = scaler.transform(alumno_row)
    else:
        if alumno_id not in matriz_base.index:
            return None
        alumno_vector_scaled = scaler.transform(matriz_base.loc[[alumno_id]])

    # 2) Cluster del alumno
    cluster_id = modelo.predict(alumno_vector_scaled)[0]

    # 3) Alumnos en ese cluster
    alumnos_similares = df_clusters.loc[df_clusters["cluster"] == cluster_id, "CODIGOALUM"]

    # 4) Subset de esos alumnos para la asignatura
    subset = df_original[
        (df_original["CODIGOALUM"].isin(alumnos_similares)) &
        (df_original["NOMBREASIGNATURA"] == asignatura_norm) &
        (df_original["NUM_CALIFICACIÓN"].notnull())
    ].copy()

    # Normalizar notas
    subset["NUM_CALIFICACIÓN"] = (
        subset["NUM_CALIFICACIÓN"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .apply(lambda x: pd.to_numeric(x, errors="coerce"))
    )

    subset = subset.dropna(subset=["NUM_CALIFICACIÓN"])

    if subset.empty:
        return 0.0

    # --- (a) Nota media normalizada
    nota_media_norm = float(subset["NUM_CALIFICACIÓN"].mean()) / 10.0

    # --- (b) Porcentaje de alumnos del cluster con nota > 0 (matriculados)
    total_alumnos_cluster = len(alumnos_similares)
    alumnos_matriculados = subset.loc[subset["NUM_CALIFICACIÓN"] > 0, "CODIGOALUM"].nunique()
    alumnos_aprobados = subset.loc[subset["NUM_CALIFICACIÓN"] >= 5, "CODIGOALUM"].nunique()
    porcentaje_matriculados = alumnos_matriculados / total_alumnos_cluster if total_alumnos_cluster > 0 else 0.0
    porcentaje_aprobados = alumnos_aprobados / alumnos_matriculados if alumnos_matriculados > 0 else 0.0
    
    #print(f"[DEBUG] {asignatura=} {cluster_id=} {total_alumnos_cluster=} {alumnos_matriculados=} {porcentaje_matriculados=:.3f} {nota_media_norm=:.3f} {alumnos_aprobados=} {porcentaje_aprobados=:.3f}")

    # --- Afinidad combinada
    afinidad = 0.45 * nota_media_norm + 0.1 * porcentaje_matriculados + 0.45 * porcentaje_aprobados

    return round(afinidad, 3)



#Saco del PDF todas las notas, el DNI y el número de expediente del alumno.
def extraer_tablas(pdf_path):
    tables = []
    lineas_extraidas = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            texto = page.extract_text()
            if texto:
                lineas = texto.split('\n')
                lineas_extraidas.extend(lineas[:5])
            page_tables = page.extract_tables()
            for table in page_tables:
                if table:  # Evita tablas vacías
                    tables.append(table)

    return tables, lineas_extraidas[1], lineas_extraidas[4]

# Rellena las asignaturas en una tabla, reemplazando None o valores vacíos por el último valor no vacío encontrado en la columna.
def rellenar_asignaturas(tabla, indice_columna=0, ultima_asignatura=None):
    "Reemplaza valores None o vacíos por el último valor no vacío encontrado en una columna."
    asignatura = ultima_asignatura
    nueva_tabla = []

    for fila in tabla:
        fila_copia = fila.copy()
        valor = fila_copia[indice_columna]

        if valor and valor.strip() and valor != "DATOS RELATIVOS A LAS ACTIVIDADES FORMATIVAS REALIZADAS EN EL CENTRO:":
            asignatura = valor.strip()
            nueva_tabla.append(fila_copia)
        else:
            # El valor es None o vacío → usar última asignatura
            
            fila_copia[indice_columna] = asignatura
            # Eliminar la fila anterior (misma asignatura)
            if nueva_tabla and nueva_tabla[-1][indice_columna] == asignatura:
                nueva_tabla.pop()
            nueva_tabla.append(fila_copia)

    return nueva_tabla, asignatura

# Limpia una tabla eliminando filas basura y rellenando asignaturas.
def limpiar_tabla(tabla, ultima_asignatura=None ,frase_objetivo="DATOS RELATIVOS A LAS ACTIVIDADES FORMATIVAS REALIZADAS EN EL CENTRO:"):
    tabla_limpia = []

    # Paso 1: eliminar filas basura
    for fila in tabla:
        if fila[0] == frase_objetivo and all(c in [None, '', ' '] for c in fila[1:]):
            continue
        tabla_limpia.append(fila)

    if not tabla_limpia:
        return [], ultima_asignatura

    # Paso 2: eliminar primera columna si todas tienen None
    if all(fila[0] is None for fila in tabla_limpia):
        tabla_limpia = [fila[1:] for fila in tabla_limpia]

    # Paso 3: rellenar asignaturas y devolver la última
    tabla_rellena, ultima_asignatura = rellenar_asignaturas(tabla_limpia, indice_columna=0, ultima_asignatura=ultima_asignatura)

    return tabla_rellena, ultima_asignatura

#Finalmente, quita columnas vacías y tablas sin asignaturas, además de la última tabla que no contiene notas.
def limpiar_tablas_finales(tablas):
    tablas_limpias = []

    for tabla in tablas:
        # Saltar si la tabla tiene 3 columnas o menos, ya que no contienen notas numéricas, por lo que no nos sirven.
        if len(tabla[0]) <= 3:
            continue

        # Eliminar filas con encabezado 'Denominación asignatura'
        tabla_sin_encabezado = [fila for fila in tabla if fila[0] != 'Denominación asignatura']

        # Saltar tablas vacías tras limpieza
        if not tabla_sin_encabezado:
            continue

        tablas_limpias.append(tabla_sin_encabezado)

    # Eliminar la última tabla si queda alguna
    if tablas_limpias:
        tablas_limpias = tablas_limpias[:-1]

    return tablas_limpias

def procesar_pdf(conn: oracledb.Connection, pdf_path: str, id: str, dni: str):
    if not id or not dni:
        raise HTTPException(status_code=400, detail="ID y DNI son obligatorios")

    tablas, dni_pdf, id_pdf = extraer_tablas(pdf_path)
    dni_pdf = dni_pdf[14:].strip().upper()
    id_pdf = id_pdf[14:].strip()

    # Comparar con lo que vino del frontend
    if dni.strip().upper() != dni_pdf:
        raise HTTPException(status_code=400, detail="El DNI no coincide con el PDF")
    if id.strip().upper() != id_pdf:
        raise HTTPException(status_code=400, detail="El ID no coincide con el PDF")

    # ✅ Guardar alumno como verificado
    guardar_alumno_verificado(conn, id_pdf, dni_pdf)

    # Procesar asignaturas del PDF
    tablas_procesadas = []
    ultima_asignatura = None
    for tabla in tablas:
        if not tabla:
            continue
        tabla_limpia, ultima_asignatura = limpiar_tabla(tabla, ultima_asignatura)
        tablas_procesadas.append(tabla_limpia)

    tablas_finales = limpiar_tablas_finales(tablas_procesadas)
    return tablas_finales


def guardar_alumno_verificado(conn:oracledb.Connection, id_alumno: str, dni: str):
    # Crear hash del DNI en mayúsculas y sin espacios
    dni_hash = hashlib.sha256(dni.strip().upper().encode()).hexdigest()
    print(f"[DEBUG] Guardando en ALUMNOS_VERIFICADOS → {id_alumno=} {dni=} {dni_hash=}")

    
    cur = conn.cursor()
    cur.execute("""
        MERGE INTO ALUMNOS_VERIFICADOS a
        USING (SELECT :id_alumno AS CODIGOALUM, :dni_hash AS DNI_HASH FROM dual) src
        ON (a.CODIGOALUM = src.CODIGOALUM)
        WHEN MATCHED THEN 
            UPDATE SET a.DNI_HASH = src.DNI_HASH
        WHEN NOT MATCHED THEN
            INSERT (CODIGOALUM, DNI_HASH) VALUES (src.CODIGOALUM, src.DNI_HASH)
    """, id_alumno=id_alumno, dni_hash=dni_hash)
    print(f"[DEBUG] Filas afectadas: {cur.rowcount}")

    conn.commit()
    return True

def existe_alumno(conn:oracledb.Connection, id_alumno:str, dni:str) -> bool:
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 
        FROM ALUMNOS_VERIFICADOS
        WHERE CODIGOALUM = :id_alumno
    """, id_alumno=id_alumno)


    return cur.fetchone()
    
    
def verificar_alumno(conn:oracledb.Connection, id_alumno: str, dni: str) -> bool:
    dni_hash = hashlib.sha256(dni.strip().upper().encode()).hexdigest()
    
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 
        FROM ALUMNOS_VERIFICADOS
        WHERE CODIGOALUM = :id_alumno AND TRIM(DNI_HASH) = :dni_hash
    """, id_alumno=id_alumno, dni_hash=dni_hash)


    return cur.fetchone() is not None


def normalizar_asignatura(nombre) -> str:
    if not isinstance(nombre, str) or not nombre.strip():
        return ""
    return nombre.replace(" ", "").strip()

def calcular_media_ponderada_alumno(cur: oracledb.Cursor, codigo_alumno: str):
    cur.execute("""
        SELECT 
            AVG(TO_NUMBER(NUM_CALIFICACIÓN)) AS media_aprobadas,
            COUNT(*) AS asignaturas_aprobadas,
            SUM(CREDITOS) AS creditos_aprobados
        FROM informes_alumno
        WHERE CODIGOALUM = :codigo
        AND CALIFICACIÓN NOT IN ('NO PRESENTADO', 'SUSPENSO')
        
    """, codigo=codigo_alumno)
    resultado = cur.fetchone() #Como esperamos solo un resultado, uso fetchone
    media, aprobadas, creditos = resultado
    if media is None or aprobadas == 0:
        return (None, 0)  # Evitamos división por cero o falta de datos
    ponderada = (media * creditos) / 240
    return (round(ponderada, 2), aprobadas) #CAMBIO: Devuelvo también la cantidad de aprobadas

def validar_pdf(file: File):
    if file.filename != 'ListadoConsultaExpedienteAcademico.pdf':
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser exactamente 'ListadoConsultaExpedienteAcademico.pdf'. No modificar el nombre del archivo tras descargar."
        )
    
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF válido.")
    
    return True

def insertar_informe_alumno(conn: oracledb.Connection, codigoalum: str, tablas_finales: list):
    cur = conn.cursor()
    for tabla in tablas_finales:
        for fila in tabla:
            try:
                nota_num = float(fila[4])
            except (ValueError, TypeError):
                nota_num = None

            try:
                creditos_num = float(fila[1])
            except (ValueError, TypeError):
                creditos_num = None

            cur.execute("""
                MERGE INTO informes_alumno dest
                USING (SELECT :codigoalum AS CODIGOALUM, :nombre AS NOMBREASIGNATURA,
                              :creditos AS CREDITOS, :curso AS CURSO_ACADEMICO,
                              :convocatoria AS CONVOCATORIA, :nota AS NUM_CALIFICACIÓN,
                              :calificacion AS CALIFICACIÓN
                       FROM dual) src
                ON (dest.CODIGOALUM = src.CODIGOALUM
                    AND dest.NOMBREASIGNATURA = src.NOMBREASIGNATURA
                    AND dest.CURSO_ACADEMICO = src.CURSO_ACADEMICO
                    AND dest.CONVOCATORIA = src.CONVOCATORIA)
                WHEN MATCHED THEN
                    UPDATE SET dest.CREDITOS = src.CREDITOS,
                               dest.NUM_CALIFICACIÓN = src.NUM_CALIFICACIÓN,
                               dest.CALIFICACIÓN = src.CALIFICACIÓN
                WHEN NOT MATCHED THEN
                    INSERT (CODIGOALUM, NOMBREASIGNATURA, CREDITOS, CURSO_ACADEMICO,
                            CONVOCATORIA, NUM_CALIFICACIÓN, CALIFICACIÓN)
                    VALUES (src.CODIGOALUM, src.NOMBREASIGNATURA, src.CREDITOS,
                            src.CURSO_ACADEMICO, src.CONVOCATORIA, src.NUM_CALIFICACIÓN, src.CALIFICACIÓN)
            """, {
                "codigoalum": codigoalum,
                "nombre": fila[0],
                "creditos": creditos_num,
                "curso": fila[2],
                "convocatoria": fila[3],
                "nota": nota_num,
                "calificacion": fila[5]
            })
    conn.commit()
    cur.close()
    return True

def obtener_informe_alumno(conn, id):
    cur = conn.cursor()
    cur.execute("""
            SELECT 
                NOMBREASIGNATURA, 
                TO_NUMBER(REPLACE(NUM_CALIFICACIÓN, ',', '.'), '999.99') AS NUM_CALIFICACION
            FROM (
                SELECT 
                    CODIGOALUM,
                    NOMBREASIGNATURA,
                    NUM_CALIFICACIÓN,
                    ROW_NUMBER() OVER (
                        PARTITION BY CODIGOALUM, NOMBREASIGNATURA 
                        ORDER BY NUM_CALIFICACIÓN DESC
                    ) AS rn
                FROM informes_alumno
                WHERE (NOMBREASIGNATURA IS NOT NULL OR NUM_CALIFICACIÓN IS NOT NULL)
            )
            WHERE CODIGOALUM = :codigo AND rn = 1

                    """, codigo = id)
    
    resultado = cur.fetchall()
    cur.close()
    
    if not resultado:
        return []
    
    return resultado

def borrar_informe_alumno(conn: oracledb.Connection, id: str):
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM informes_alumno
        WHERE CODIGOALUM = :codigo
    """, codigo=id)
    conn.commit()
    cur.close()
    
def borrar_alumno_verificado(conn:oracledb.Connection, id: str):
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM ALUMNOS_VERIFICADOS
        WHERE CODIGOALUM = :codigo
    """, codigo=id)
    conn.commit()
    cur.close()

def obtener_optativas_por_titulacion(id: str, conn: oracledb.Connection):
    titulacion_id = id[:4]
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT NOMBRE
        FROM v_optativas
        WHERE TITULACION = :titulacion
        AND NOMBRE IS NOT NULL
        AND UPPER(OFERTADA) IN ('SÍ', 'SI')
    """, titulacion=titulacion_id)
    
    asignaturas = cur.fetchall()
    cur.close()
    
    if not asignaturas:
        return []
    
    return asignaturas

def check_admin(conn: oracledb.Connection, user: str, password: str):
    cur = conn.cursor()
    cur.execute("""
        SELECT VALIDA_USUARIO(:p_user, :p_password) AS resultado FROM dual
    """, p_user=user, p_password=password)
    
    resultado = cur.fetchone()[0] 
    cur.close()
    
    return resultado

def numero_consultas_titulaciones(conn: oracledb.Connection):
    cur = conn.cursor()
    cur.execute("""
            SELECT TITULACION, COUNT(*) AS TOTAL_CONSULTAS
            FROM ADMIN_INFO
            GROUP BY TITULACION
            ORDER BY TOTAL_CONSULTAS DESC
            FETCH FIRST 5 ROWS ONLY
            """)
    titulaciones = cur.fetchall()
    print(titulaciones)
    cur.close()
    
    if not titulaciones:
        return []
    
    return titulaciones

def asignaturas_populares(conn: oracledb.Connection):
    cur = conn.cursor()
    cur.execute("""
        SELECT NOMBREASIGNATURA, COUNT(*) AS TOTAL_CONSULTAS
        FROM ADMIN_INFO
        GROUP BY NOMBREASIGNATURA
        ORDER BY TOTAL_CONSULTAS DESC
        FETCH FIRST 5 ROWS ONLY
    """)
    asignaturas = cur.fetchall()
    cur.close()
    
    if not asignaturas:
        return []
    
    return asignaturas

def asignaturas_afinidad(conn: oracledb.Connection):
    cur = conn.cursor()
    cur.execute("""
        SELECT NOMBREASIGNATURA, AVG(AFINIDAD) AS AFINIDAD_MEDIA
        FROM ADMIN_INFO
        GROUP BY NOMBREASIGNATURA
        ORDER BY AFINIDAD_MEDIA DESC
        FETCH FIRST 5 ROWS ONLY
    """)
    asignaturas = cur.fetchall()
    cur.close()
    
    if not asignaturas:
        return []
    
    return asignaturas
    

def asignaturas_probabilidad(conn: oracledb.Connection):
    cur = conn.cursor()
    cur.execute("""
        SELECT NOMBREASIGNATURA, AVG(PROBABILIDAD) AS PROB_MEDIA
        FROM ADMIN_INFO
        GROUP BY NOMBREASIGNATURA
        ORDER BY PROB_MEDIA DESC
        FETCH FIRST 5 ROWS ONLY
    """)
    asignaturas = cur.fetchall()
    cur.close()
    
    if not asignaturas:
        return []
    
    return asignaturas

def insertar_afinidad_alumno(conn: oracledb.Connection, alumno_id: str, asignatura: str, afinidad: float):
    titulacion = alumno_id[:4]  # Asumiendo que los primeros 4 caracteres son la titulación
    cur = conn.cursor()
    cur.execute("""
    MERGE INTO ADMIN_INFO ai
    USING (SELECT :alumno AS ID_ALUMNO, :asignatura AS NOMBREASIGNATURA FROM dual) src
    ON (ai.ID_ALUMNO = src.ID_ALUMNO AND ai.NOMBREASIGNATURA = src.NOMBREASIGNATURA)
    WHEN MATCHED THEN
        UPDATE SET AFINIDAD = :afinidad
    WHEN NOT MATCHED THEN
        INSERT (ID_ALUMNO, NOMBREASIGNATURA, TITULACION, AFINIDAD)
        VALUES (:alumno, :asignatura, :titulacion, :afinidad)
""", alumno=alumno_id, asignatura=asignatura, titulacion=titulacion, afinidad=afinidad)
    conn.commit()
    cur.close()
    
    return True

def insertar_probabilidad_alumno(conn: oracledb.Connection, alumno_id: str, asignatura: str, probabilidad: float):
    titulacion = alumno_id[:4]  # Asumiendo que los primeros 4 caracteres son la titulación
    cur = conn.cursor()
    cur.execute("""
    MERGE INTO ADMIN_INFO ai
    USING (SELECT :alumno AS ID_ALUMNO, :asignatura AS NOMBREASIGNATURA FROM dual) src
    ON (ai.ID_ALUMNO = src.ID_ALUMNO AND ai.NOMBREASIGNATURA = src.NOMBREASIGNATURA)
    WHEN MATCHED THEN
        UPDATE SET PROBABILIDAD = :prob
    WHEN NOT MATCHED THEN
        INSERT (ID_ALUMNO, NOMBREASIGNATURA, TITULACION, PROBABILIDAD)
        VALUES (:alumno, :asignatura, :titulacion, :prob)
    """, alumno=alumno_id, asignatura=asignatura, titulacion=titulacion, prob=probabilidad)

    conn.commit()
    cur.close()
    
    return True

def reiniciar_admin_db(conn: oracledb.Connection):
    cur = conn.cursor()
    cur.execute(""" 
                DELETE FROM ADMIN_INFO
                """)
    conn.commit()
    cur.close()
    
    return True

def obtener_asignatura_sin_normalizar(conn: oracledb.Connection, asignatura: str):
    cur = conn.cursor()
    cur.execute(""" 
                SELECT DISTINCT NOMBREASIGNATURA
                FROM V_CALIFICACIONES
                WHERE REPLACE(NOMBREASIGNATURA, ' ', '') = :asignatura
                """, asignatura=asignatura)
    resultado = cur.fetchone()
    if resultado is None:
        raise HTTPException(status_code=400, detail=f"No se ha encontrado la asignatura {asignatura}")
    cur.close()
    asignatura = resultado[0]

    return asignatura