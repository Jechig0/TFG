#Rutas relacionadas con alumnos (notas, media, etc.)
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import oracledb
import funciones as funciones

#Creamos el router para las rutas de alumnos
alumnoRouter = APIRouter()

#Dirección de la base de datos a la que se va a acceder en las peticiones
dsn = oracledb.makedsn("afrodita.lcc.uma.es", 1521, sid="APOLO")

@alumnoRouter.get("/alumno/{id}", tags=["Alumno"])
def get_alumno_by_id(id:str):
    global df
    #Creo la conexión y el cursor, y ejecuto la consulta
    conn = oracledb.connect(user="tfm_puertas", password="JCGRmlbEsc", dsn=dsn)
    #La subconsulta, que se reutiliza en el codigo, agrupa todas las notas de la base de datos de los alumnos y las asignaturas, y devuelve solo la más alta
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
            FROM v_calificaciones
            WHERE 
                (NOMBREASIGNATURA IS NOT NULL 
                OR NUM_CALIFICACIÓN IS NOT NULL)
            )
        WHERE CODIGOALUM = :codigo AND rn = 1
            """, codigo = id)
    resultado = cur.fetchall()
    conn.close()
    
    if not resultado:
        df_filtrado = df[df["CODIGOALUM"] == id]
        resultado = df_filtrado[["NOMBRE_ORIGINAL", "NUM_CALIFICACIÓN"]].values.tolist()

    #Si no se encuentra el alumno, se devuelve error
    if not resultado:
        raise HTTPException(status_code=400, detail=f"No se encontró información para el alumno con código {id}")
    
    return JSONResponse(status_code=200, content=jsonable_encoder(resultado))