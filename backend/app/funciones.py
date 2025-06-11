# Añadimos todas las librerias necesarias
import oracledb as oracledb
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def calcular_media_ponderada(cur, codigo_alumno, curso_max):
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
    # Fórmula: (media * aprobadas * 6) / 240. NOTA: Supongo que todas las asignaturas valen 6 créditos ya que no tenemos información de cada una
    ponderada = (media * creditos) / 240
    return (round(ponderada, 2), aprobadas) #CAMBIO: Devuelvo también la cantidad de aprobadas
    
def obtener_alumnos_matriculados(cur, nombre_asignatura):
        cur.execute("""
            SELECT DISTINCT CODIGOALUM, CURSOACADÉMICO
            FROM v_calificaciones
            WHERE NOMBREASIGNATURA = :asignatura
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
                    print(media, ',', codigo_alum)
                    medias.append(media)
        if medias:
            nota_corte_por_año[curso_acad] = min(medias)

    return nota_corte_por_año  # Dict: { "2018-19": 6.25, "2019-20": 5.8, ... }

def calcular_probabilidad_entrada(cur, nombre_asignatura, codigo_alumno):
    # Obtener las notas de corte por año
    notas_corte = calcular_nota_corte(cur, nombre_asignatura)
    print(notas_corte)

    if not notas_corte:
        return 0.0  # No hay base para calcular probabilidad

    total = 0
    supera = 0

    media_alumno, aprobadas = calcular_media_ponderada(cur, codigo_alumno, '2022-23')
    print(media_alumno)
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

# Suponemos que tienes un DataFrame con columnas: ['CODIGOALUM', 'NOMBREASIGNATURA', 'NUM_CALIFICACIÓN']
df = pd.read_csv("data.csv")
def entrenar_clustering(df, n_clusters=12):
    # Crear matriz alumno-asignatura
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

def predecir_afinidad_cluster(alumno_id, asignatura, modelo, scaler, matriz, df_clusters, df_original):
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

