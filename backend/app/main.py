#Importaciones necesarias en main.
import math
import os
import tempfile
import oracledb as oracledb
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse
import funciones 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import pandas as pd
from routers.alumno import alumnoRouter
from routers.asignatura import asignaturaRouter


#Inicialización de la aplicación FastAPI
app = FastAPI(
    title='FastAPI', #Título que aparecerá en la documentación
    description="API Recomendador Asignaturas", #Descripción debajo del título
    version='1.0.0', #Número de la etiqueta gris al lado del título
)

#Configuración de CORS para permitir peticiones desde cualquier origen (para el trabajo en desarrollo, que solo se ejecuta en localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alumnoRouter)
app.include_router(asignaturaRouter)

#Dirección de la base de datos a la que se va a acceder en las peticiones
dsn = oracledb.makedsn("afrodita.lcc.uma.es", 1521, sid="APOLO")
conn = oracledb.connect(user="tfm_puertas", password="JCGRmlbEsc", dsn=dsn)

# Variables globales
df = funciones.crear_df(conn)
pdf_info: list = []

# Redirección a la documentación de FastAPI al acceder a la raíz
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url='/docs')

@app.get("/media/{id}", tags=["Alumno"])
def get_media(id:str):
    global df, pdf_info
    conn = oracledb.connect(user="tfm_puertas", password="JCGRmlbEsc", dsn=dsn)
    cur = conn.cursor()
    media = funciones.calcular_media_ponderada(cur, id, "2024-25")[0]
    conn.close()
    if media is None:
        media = funciones.calcular_media_ponderada_df(df, pdf_info, id)[0]
        print(f'Media calculada desde el DataFrame: {media}')
    if media is None or math.isnan(media):
        raise HTTPException(status_code=400, detail=f'No se ha podido calcular la media de {id}')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(media))

@app.get("/asignaturas/{id}", tags=['Asignatura'])
def get_asignatura(id:str):
    conn = oracledb.connect(user="tfm_puertas", password="JCGRmlbEsc", dsn=dsn)
    asignaturas = funciones.obtener_optativas_por_titulación(id, conn)
    conn.close()
    if not asignaturas:
        raise HTTPException(status_code=400, detail='No se han podido obtener las asignaturas')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(asignaturas))

@app.get("/probabilidadEntrada/{alumnoId}/{asignatura}", tags=['Asignatura'])
def get_probabilidad_acceso(alumnoId: str, asignatura: str):
    print(f'Entrada al Enpoint con {asignatura}')
    global df, pdf_info
    conn = oracledb.connect(user="tfm_puertas", password="JCGRmlbEsc", dsn=dsn)
    cur = conn.cursor()
    probabilidad = funciones.calcular_probabilidad_entrada(cur, asignatura, alumnoId, df, pdf_info)
    conn.close()
    return JSONResponse(status_code=200, content=jsonable_encoder(probabilidad))

@app.get("/afinidad/{alumnoId}/{asignatura}", tags=['Afinidad'])
def get_afinidad(alumnoId: str, asignatura: str):
    global df
    conn = oracledb.connect(user="tfm_puertas", password="JCGRmlbEsc", dsn=dsn)
    modelo, scaler, matriz, df_clusters = funciones.entrenar_clustering(df)
    afinidad = funciones.predecir_afinidad_cluster(alumnoId, asignatura, modelo, scaler, matriz, df_clusters, df)
    conn.close()
    if (afinidad is None):
        return(JSONResponse(status_code=400, detail="No se ha encontrado al alumno"))
    return JSONResponse(status_code=200, content=jsonable_encoder(afinidad))

@app.post("/alumno/{id}/subir-informe", tags=["Alumno"])
async def procesar_pdf(id: str, file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf') and not file.filename.startswith('ListadoConsultaExpedienteAcademico'):
        raise HTTPException(status_code=400, detail="El archivo no es un PDF válido.")
    global df, pdf_info
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(await file.read())
        temp_pdf_path = temp_pdf.name

    tablas_finales = funciones.procesar_pdf(temp_pdf_path)
    df_alumno = funciones.convertir_pdf_a_df(tablas_finales, id)
    df = pd.concat([df, df_alumno], ignore_index=True)
    df = df.drop_duplicates(subset=["CODIGOALUM", "NOMBREASIGNATURA"], keep="last").reset_index(drop=True)
    pdf_info = tablas_finales
    # Construir respuesta: nombre de asignatura + nota literal
    resultado_dict = {}

    for tabla in tablas_finales:
        for fila in tabla:
            if len(fila) >= 6:
                asignatura = fila[0]
                nota = fila[4]
                resultado_dict[asignatura] = {
                    "asignatura": asignatura,
                    "nota": nota
                }

# Convertir de vuelta a lista
    resultado = list(resultado_dict.values())

    os.remove(temp_pdf_path)
    if(resultado == []):
        return JSONResponse(status_code=400, content={"detail": "No se encontraron asignaturas con notas en el PDF proporcionado."})
    return JSONResponse(status_code=201, content=jsonable_encoder(resultado))