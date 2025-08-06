#Guardamos las funciones que se usan en el backend de la aplicación para la gestión de alumnos y asignaturas.

# Añadimos todas las librerias necesarias
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
    # Obtener las notas de corte por año
    notas_corte = calcular_nota_corte(cur, nombre_asignatura)
    if not notas_corte:
        raise HTTPException(status_code=400, detail=f"No hay datos para la asignatura {nombre_asignatura}")

    total = 0
    supera = 0

    probabilidad = calcular_probabilidad_entrada_alumno(cur, nombre_asignatura, codigo_alumno, notas_corte)

    #Si estamos usando un alumno de la vista, se ejecuta este bloque
    if probabilidad == 0 or probabilidad is None:
        media_alumno, aprobadas = calcular_media_ponderada_vista(cur, codigo_alumno, '2022-23')
        for curso_acad, nota_corte in notas_corte.items():
        
            if media_alumno is not None:
                total += 1
                if media_alumno > nota_corte:
                    supera += 1
        
    probabilidad = (supera / total) * 100
    return round(probabilidad, 2)

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
    
def entrenar_clustering(df:pd.DataFrame, n_clusters=12):
    # Crear matriz alumno-asignatura
    df['NUM_CALIFICACIÓN'] = pd.to_numeric(df['NUM_CALIFICACIÓN'], errors='coerce')
    matriz = df.pivot_table(index='CODIGOALUM', columns='NOMBREASIGNATURA', values='NUM_CALIFICACIÓN')
    matriz = matriz.fillna(0)  #Para evitar valores NaN
    
    scaler = StandardScaler()
    matriz_escalada = scaler.fit_transform(matriz)
    
    modelo = KMeans(n_clusters=n_clusters, random_state=42)
    modelo.fit(matriz_escalada)
    
    # Añadir etiquetas de cluster
    df_clusters = pd.DataFrame(matriz.index, columns=['CODIGOALUM'])
    df_clusters['cluster'] = modelo.labels_
    
    return modelo, scaler, matriz, df_clusters

def predecir_afinidad_cluster(alumno_id:str, asignatura:str, modelo:KMeans, scaler:StandardScaler, matriz:pd.DataFrame, df_clusters:pd.DataFrame, df_original:pd.DataFrame):
    if alumno_id not in matriz.index or asignatura not in matriz.columns:
        return None
    
    alumno_vector = scaler.transform(matriz.loc[[alumno_id]])
    cluster_id = modelo.predict(alumno_vector)[0]
    
    # Alumnos en ese cluster
    alumnos_similares = df_clusters[df_clusters['cluster'] == cluster_id]['CODIGOALUM']
    
    # Notas en la asignatura de ese grupo
    notas = df_original[
        (df_original['CODIGOALUM'].isin(alumnos_similares)) &
        (df_original['NOMBREASIGNATURA'] == asignatura) &
        (df_original['NUM_CALIFICACIÓN'].notnull())
    ]['NUM_CALIFICACIÓN'].astype(float)
    
    if notas.empty:
        return 0.0
    
    return round(notas.mean() / 10, 3)

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

def procesar_pdf(pdf_path, id:str, dni:str):
    if not id or not dni:
        raise HTTPException(status_code=400, detail='No se han proporcionado DNI o ID válidos.')
    tablas, dni_pdf, id_pdf = extraer_tablas(pdf_path)
    dni_pdf = dni_pdf[14:]
    id_pdf = id_pdf[14:]
    
    if dni_pdf.strip() != dni.upper():
        raise HTTPException(status_code=400, detail=f'El DNI no coincide.')
    
    if id_pdf.strip() != id.upper():
        raise HTTPException(status_code=400, detail=f'El ID no coincide.')
    tablas_procesadas = []
    ultima_asignatura = None

    for tabla in tablas:
        if not tabla:
            continue
        tabla_limpia, ultima_asignatura = limpiar_tabla(tabla, ultima_asignatura)
        tablas_procesadas.append(tabla_limpia)
    tablas_finales = limpiar_tablas_finales(tablas_procesadas)

    
    return tablas_finales

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

    
def calcular_probabilidad_entrada_alumno(cur: oracledb.Cursor, nombre_asignatura: str, codigo_alumno: str, notas_corte: dict = None, df: pd.DataFrame = None, pdf_info: list = None):

    media_alumno, aprobadas = calcular_media_ponderada_alumno(cur, codigo_alumno)
    total = 0
    supera = 0
    #media_alumno = 0.15
    for curso_acad, nota_corte in notas_corte.items():
            total += 1
            if media_alumno > nota_corte:
                supera += 1

    if total == 0:
        return 0.0  # El alumno no tiene historial válido

    probabilidad = (supera / total) * 100
    return round(probabilidad, 2)

def obtener_optativas_por_titulación(id: str, conn: oracledb.Connection):
    titulacion = int(id[:4])
    cur = conn.cursor()
    cur.execute("""
                SELECT nombre
                FROM v_optativas
                WHERE titulacion = :titulacion_alumno AND UPPER(ofertada) IN ('SI', 'SÍ')
                """, titulacion_alumno=titulacion)
    optativas = cur.fetchall()
    return optativas

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
                nota_num = None  # o salta esta fila si es inválida

            try:
                creditos_num = float(fila[1])
            except (ValueError, TypeError):
                creditos_num = None  # lo mismo
            cur.execute("""
                INSERT INTO informes_alumno
                (
                CODIGOALUM, NOMBREASIGNATURA, CREDITOS, CURSO_ACADÉMICO,
                CONVOCATORIA, NUM_CALIFICACIÓN, CALIFICACIÓN
                ) VALUES (:1, :2, :3, :4, :5, :6, :7)
""", (codigoalum, fila[0], creditos_num, fila[2], fila[3], nota_num, fila[5]))
    conn.commit()
    cur.close()
    return True

def obtener_informe_alumno(conn, id):
    cur = conn.cursor()
    cur.execute("""
                SELECT NOMBREASIGNATURA, NUM_CALIFICACIÓN
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
                    WHERE 
                        (NOMBREASIGNATURA IS NOT NULL 
                        OR NUM_CALIFICACIÓN IS NOT NULL)
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