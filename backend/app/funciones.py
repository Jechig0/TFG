# Añadimos todas las librerias necesarias
import oracledb as oracledb
import pandas as pd
import pdfplumber
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def calcular_media_ponderada(cur: oracledb.Cursor, codigo_alumno, curso_max):
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
            resultado = calcular_media_ponderada(cur, codigo_alum, curso_acad)
            if resultado:
                media, aprobadas = resultado
                if media is not None and aprobadas > 10:
                    medias.append(media)
        if medias:
            nota_corte_por_año[curso_acad] = min(medias)

    return nota_corte_por_año  # Dict: { "2018-19": 6.25, "2019-20": 5.8, ... }

def calcular_probabilidad_entrada(cur, nombre_asignatura, codigo_alumno, df, pdf_info):
    # Obtener las notas de corte por año
    notas_corte = calcular_nota_corte(cur, nombre_asignatura)
    if not notas_corte:
        return 0.0  # No hay base para calcular probabilidad

    total = 0
    supera = 0

    media_alumno, aprobadas = calcular_media_ponderada(cur, codigo_alumno, '2022-23')
    #media_alumno = 0.15
    for curso_acad, nota_corte in notas_corte.items():
        
        if media_alumno is not None:
            total += 1
            if media_alumno > nota_corte:
                supera += 1

    if total == 0:
        return calcular_probabilidad_entrada_df(notas_corte, df, codigo_alumno, pdf_info)

    probabilidad = (supera / total) * 100
    return round(probabilidad, 2)

def crear_df(conn: oracledb.Connection):
    sql = """SELECT CODIGOALUM, REPLACE(NOMBREASIGNATURA, ' ', '') AS NOMBREASIGNATURA,  NOMBREASIGNATURA AS NOMBRE_ORIGINAL, NUM_CALIFICACIÓN
FROM (
    SELECT 
        CODIGOALUM,
        REPLACE(NOMBREASIGNATURA, ' ', '') AS NOMBREASIGNATURA,
        NOMBREASIGNATURA AS NOMBRE_ORIGINAL,
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

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page.extract_text()
            page_tables = page.extract_tables()
            for table in page_tables:
                if table:  # Evita tablas vacías
                    tables.append(table)

    return tables

def rellenar_asignaturas(tabla, indice_columna=0):
    "Reemplaza valores None o vacíos por el último valor no vacío encontrado en una columna."
    ultima_asignatura = None
    nueva_tabla = []

    for fila in tabla:
        fila_copia = fila.copy()
        valor = fila_copia[indice_columna]

        if valor and valor.strip():
            ultima_asignatura = valor.strip()
            nueva_tabla.append(fila_copia)
        else:
            # El valor es None o vacío → usar última asignatura
            fila_copia[indice_columna] = ultima_asignatura
            # Eliminar la fila anterior (misma asignatura)
            if nueva_tabla and nueva_tabla[-1][indice_columna] == ultima_asignatura:
                nueva_tabla.pop()
            nueva_tabla.append(fila_copia)

    return nueva_tabla

def limpiar_tabla(tabla, frase_objetivo="DATOS RELATIVOS A LAS ACTIVIDADES FORMATIVAS REALIZADAS EN EL CENTRO:"):
    tabla_limpia = []

    # Paso 1: eliminar filas basura que solo tienen la frase y Nones
    for fila in tabla:
        if fila[0] == frase_objetivo and all(c in [None, '', ' '] for c in fila[1:]):
            continue
        tabla_limpia.append(fila)

    if not tabla_limpia:
        return []

    # Paso 2: eliminar la primera columna si todas las filas empiezan con None
    if all(fila[0] == None for fila in tabla_limpia):
        tabla_limpia = [fila[1:] for fila in tabla_limpia]

    # Paso 3: rellenar los Nones en la columna de asignaturas (columna 0)
    return rellenar_asignaturas(tabla_limpia, indice_columna=0)

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

def procesar_pdf(pdf_path):
    tablas = extraer_tablas(pdf_path)
    tablas_limpias = [limpiar_tabla(tabla) for tabla in tablas]
    tablas_finales = limpiar_tablas_finales(tablas_limpias)

    
    return tablas_finales

def normalizar_asignatura(nombre: str) -> str:
    return nombre.replace(" ", "").strip()

def convertir_pdf_a_df(lista_tablas, codigo_alumno):
    datos_limpios = []

    for tabla in lista_tablas:
        for fila in tabla:
            asignatura = normalizar_asignatura(fila[0])
            asignatura_original = fila[0]  # Mantener el nombre original
            nota = fila[4]

            if not asignatura or not nota:
                continue

            datos_limpios.append({
                "CODIGOALUM": codigo_alumno,
                "NOMBREASIGNATURA": asignatura,
                "NOMBRE_ORIGINAL": asignatura_original,
                "NUM_CALIFICACIÓN": nota
            })

    return pd.DataFrame(datos_limpios)

def calcular_media_ponderada_df(df: pd.DataFrame, tablas_pdf: list, codigo_alumno: str):
    total_creditos = 0

    for tabla in tablas_pdf:
        for fila in tabla:
            if len(fila) < 6:
                continue

            asignatura = fila[0]
            creditos = fila[1]
            curso = fila[2]
            nota_str = fila[4]
            calificacion_literal = fila[5]

            # Validar datos necesarios
            if not asignatura or not nota_str or not creditos or not curso or not calificacion_literal:
                continue

            # Validar calificación aprobada
            calif_normalizada = calificacion_literal.strip().upper()
            if calif_normalizada in ["SUSPENSO", "NO PRESENTADO"]:
                continue
            total_creditos = float(creditos) + total_creditos

    # Filtrar registros del DF
    df_filtrado = df[
        (df["CODIGOALUM"] == codigo_alumno) &
        (df["NUM_CALIFICACIÓN"].astype(float) >= 5)
    ]
        
    try:
        notas_df = df_filtrado["NUM_CALIFICACIÓN"].astype(float)
        media_df = notas_df.mean()
        aprobadas_df = len(df_filtrado)
        
    except Exception:
        media_df = None
        total_creditos = 0
        aprobadas_df = 0
        
    # Agregar datos del PDF

    ponderada = round((media_df) * (total_creditos / 240), 2)
    return (ponderada, aprobadas_df)

    
def calcular_probabilidad_entrada_df(notas_corte: dict, df: pd.DataFrame ,codigo_alumno: str, datos_pdf: list):

    media_alumno, aprobadas = calcular_media_ponderada_df(df, datos_pdf , codigo_alumno)
    total = 0
    supera = 0
    #media_alumno = 0.15
    for curso_acad, nota_corte in notas_corte.items():
        
        if media_alumno is not None:
            total += 1
            if media_alumno > nota_corte:
                supera += 1

    if total == 0:
        return 0.0  # El alumno no tiene historial válido

    probabilidad = (supera / total) * 100
    return round(probabilidad, 2)