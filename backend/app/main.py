import os
import tempfile
import oracledb as oracledb
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse
import funciones 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import pandas as pd


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
conn = oracledb.connect(user="tfm_puertas", password="JCGRmlbEsc", dsn=dsn)
df = funciones.crear_df(conn)
pdf_info: list = []


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url='/docs')

@app.get("/alumno/{id}", tags=["Alumno"])
def get_alumno_by_id(id:str):
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
    
    #Si no se encuentra el alumno, se devuelve error
    if not resultado:
        raise HTTPException(status_code=400, detail=f"No se encontró información para el alumno con código {id}")
    
    return JSONResponse(status_code=200, content=jsonable_encoder(resultado))

@app.get("/media/{id}", tags=["Alumno"])
def get_media(id:str):
    conn = oracledb.connect(user="tfm_puertas", password="JCGRmlbEsc", dsn=dsn)
    cur = conn.cursor()
    media, aprobadas = funciones.calcular_media_ponderada(cur, id, "2024-25")
    conn.close()
    if media is None:
        raise HTTPException(status_code=400, detail=f'No se ha podido calcular la media de {id}')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(media))

@app.get("/asignaturas", tags=['Asignatura'])
def get_asignatura():
    conn = oracledb.connect(user="tfm_puertas", password="JCGRmlbEsc", dsn=dsn)
    cur = conn.cursor()
    #Al hacer la consulta en sql, hay una asignatura null. La quito de los resultados
    cur.execute("SELECT distinct nombreasignatura FROM v_calificaciones WHERE nombreasignatura IS NOT NULL")
    asignaturas = cur.fetchall()
    conn.close()
    if not asignaturas:
        raise HTTPException(status_code=500, detail='No se han podido obtener las asignaturas')
    
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
    print('Afinidad llamada...')
    global df
    df_filtrado = df[
        (df["CODIGOALUM"] == alumnoId) &
        (df["NUM_CALIFICACIÓN"].astype(float) >= 5)
    ]
    print(df_filtrado)
    conn = oracledb.connect(user="tfm_puertas", password="JCGRmlbEsc", dsn=dsn)
    modelo, scaler, matriz, df_clusters = funciones.entrenar_clustering(df)
    afinidad = funciones.predecir_afinidad_cluster(alumnoId, asignatura, modelo, scaler, matriz, df_clusters, df)
    conn.close()
    print('Afinidad terminada')
    if (afinidad is None):
        return(JSONResponse(status_code=400, detail="No se ha encontrado al alumno"))
    return JSONResponse(status_code=200, content=jsonable_encoder(afinidad))

@app.post("/alumno/{id}/subir-informe", tags=["Alumno"])
async def procesar_pdf(id: str, file: UploadFile = File(...)):
    global df, pdf_info
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(await file.read())
        temp_pdf_path = temp_pdf.name

    tablas_finales = funciones.procesar_pdf(temp_pdf_path)
    df_alumno = funciones.convertir_pdf_a_df(tablas_finales, id)
    df = pd.concat([df, df_alumno], ignore_index=True)
    pdf_info = tablas_finales
    # Construir respuesta: nombre de asignatura + nota literal
    resultado = []
    for tabla in tablas_finales:
        for fila in tabla:
            if len(fila) >= 6:
                resultado.append({
                    "asignatura": fila[0],
                    "nota": fila[4]
                })

    os.remove(temp_pdf_path)
    if(resultado == []):
        return JSONResponse(status_code=400, content={"detail": "No se encontraron asignaturas con notas en el PDF proporcionado."})
    return JSONResponse(status_code=201, content=jsonable_encoder(resultado))