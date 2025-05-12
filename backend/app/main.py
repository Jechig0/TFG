import oracledb as oracledb
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from calculo_acceso import calcular_media_ponderada
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

@app.get("/", tags=["Inicio"])
def root():
    return HTMLResponse("<h2>Hola mundo</h2>")

@app.get("/alumno/{id}", tags=["Alumno"])
def get_alumno_by_id(id:str):
    conn = oracledb.connect(user="tfm_puertas", password="JCGRmlbEsc", dsn=dsn)
    cur = conn.cursor()
    cur.execute("""
                SELECT codigoalum, nombreasignatura, num_calificación
                FROM v_calificaciones
                WHERE codigoalum = :codigo
                """, codigo = id)
    resultado = cur.fetchall()
    conn.close()
    return JSONResponse(status_code=200, content=jsonable_encoder(resultado))