import oracledb as oracledb
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from funciones import calcular_media_ponderada
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder


app = FastAPI(
    title='FastAPI', #Título que aparecerá en la documentación
    description="API Recomendador Asignaturas", #Descripción debajo del título
    version='1.0.0', #Número de la etiqueta gris al lado del título
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Dirección de la base de datos a la que se va a acceder en las peticiones
dsn = oracledb.makedsn("afrodita.lcc.uma.es", 1521, sid="APOLO")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url='/docs')

@app.get("/alumno/{id}", tags=["Alumno"])
def get_alumno_by_id(id:str):
    #Creo la conexión y el cursor, y ejecuto la consulta
    conn = oracledb.connect(user="tfm_puertas", password="JCGRmlbEsc", dsn=dsn)
    cur = conn.cursor()
    cur.execute("""
                SELECT nombreasignatura, num_calificación
                FROM v_calificaciones
                WHERE codigoalum = :codigo
                """, codigo = id)
    resultado = cur.fetchall()
    conn.close()
    
    #Si no se encuentra el alumno, se devuelve error
    if not resultado:
        raise HTTPException(status_code=404, detail=f"No se encontró información para el alumno con código {id}")
    
    return JSONResponse(status_code=200, content=jsonable_encoder(resultado))

@app.get("/media/{id}", tags=["Alumno"])
def get_media(id:str):
    conn = oracledb.connect(user="tfm_puertas", password="JCGRmlbEsc", dsn=dsn)
    cur = conn.cursor()
    media = calcular_media_ponderada(cur, id, "2024-25")
    conn.close()
    if media is None:
        raise HTTPException(status_code=404, detail=f'No se ha podido calcular la media de {id}')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(media))

@app.get("/asignaturas", tags=['Asignatura'])
def get_asignatura():
    conn = oracledb.connect(user="tfm_puertas", password="JCGRmlbEsc", dsn=dsn)
    cur = conn.cursor()
    cur.execute("select distinct nombreasignatura from v_calificaciones")
    asignaturas = cur.fetchall()
    conn.close()
    if not asignaturas:
        raise HTTPException(status_code=500, detail='No se han podido obtener las asignaturas')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(asignaturas))
