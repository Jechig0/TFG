# Añadimos todas las librerias necesarias
import oracledb as oracledb
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def calcular_media_ponderada(cur:oracledb.Cursor, codigo_alumno:str, curso_max:str):
    #Consulta para devolver la media hasta cierto año (esto es útil para integrarlo con siguientes funciones)
    cur.execute("""
        SELECT 
            AVG(TO_NUMBER(NUM_CALIFICACIÓN)) AS media_aprobadas,
            COUNT(*) AS asignaturas_aprobadas
        FROM v_calificaciones
        WHERE CODIGOALUM = :codigo
        AND CALIFICACIÓN NOT IN ('NO PRESENTADO', 'SUSPENSO')
        AND nombreasignatura IS NOT NULL
        AND TO_NUMBER(SUBSTR(CURSOACADÉMICO, 1, 4)) < TO_NUMBER(SUBSTR(:curso_inicio , 1, 4))
    """, codigo=codigo_alumno, curso_inicio=curso_max[:4])

    resultado = cur.fetchone() #Como esperamos solo un resultado, uso fetchone
    media, aprobadas = resultado

    #Si la media devuelve None o todas las asignaturas de la base de datos están suspensas, devuelve None
    if media is None or aprobadas == 0:
        return None  # Evitamos división por cero o falta de datos

    # Fórmula: (media * aprobadas * 6) / 240. NOTA: Supongo que todas las asignaturas valen 6 créditos ya que no tenemos información de cada una
    ponderada = (media * aprobadas * 6) / 240
    return round(ponderada, 2)
    
def obtener_alumnos_matriculados(cur, nombre_asignatura):
        cur.execute("""
            SELECT DISTINCT CODIGOALUM, CURSOACADÉMICO
            FROM v_calificaciones
            WHERE NOMBREASIGNATURA = :asignatura
        """, asignatura=nombre_asignatura)

        return cur.fetchall()

def calcular_nota_corte(conn, nombre_asignatura):
    # 1. Obtener alumnos + curso académico donde cursaron esa asignatura
    alumnos_con_curso = obtener_alumnos_matriculados(conn, nombre_asignatura)

    # 2. Agrupar alumnos por curso académico
    cursos = {}
    for codigo_alum, curso_acad in alumnos_con_curso:
        cursos.setdefault(curso_acad, []).append(codigo_alum)

    # 3. Para cada curso, calcular la nota de corte
    nota_corte_por_anio = {}

    for curso_acad, codigos_alumnos in cursos.items():
        medias = []
        for codigo_alum in codigos_alumnos:
            media = calcular_media_ponderada(conn, codigo_alum, curso_acad)
            if media is not None:
                #print(media, ',', curso_acad) #Para ver las medias ponderadas con el año al que pertenecen
                medias.append(media)
        
        if medias:
            nota_corte_por_anio[curso_acad] = min(medias)

    return nota_corte_por_anio  # Dict: { "2018-19": 6.25, "2019-20": 5.8, ... }

def calcular_probabilidad_entrada(conn, nombre_asignatura, codigo_alumno):
    # Obtener las notas de corte por año
    notas_corte = calcular_nota_corte(conn, nombre_asignatura)
    print(notas_corte)

    if not notas_corte:
        return 0.0  # No hay base para calcular probabilidad

    total = 0
    supera = 0

    media_alumno = calcular_media_ponderada(conn, codigo_alumno, '2022-23')
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