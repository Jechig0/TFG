#Rutas relacionadas con alumnos (notas, media, etc.)

#Añadir las importaciones necesarias
import math
import os
import tempfile
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import oracledb
import pandas as pd
import funciones as funciones

#Creamos el router para las rutas de alumnos, colocando el prefijo "/alumno" para todas las rutas
alumnoRouter = APIRouter(prefix="/alumno", tags=["Alumno"])

@alumnoRouter.get("/{id}")
def get_alumno_by_id(id:str, request: Request):
    pool: oracledb.ConnectionPool = request.app.state.pool
    df: pd.DataFrame = request.app.state.df
    #La subconsulta, que se reutiliza en el codigo, agrupa todas las notas de la base de datos de los alumnos y las asignaturas, y devuelve solo la más alta
    with pool.acquire() as conn:
        with conn.cursor() as cur:
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
            cur.close()
    
    if not resultado:
        df_filtrado = df[df["CODIGOALUM"] == id]
        resultado = df_filtrado[["NOMBRE_ORIGINAL", "NUM_CALIFICACIÓN"]].values.tolist()

    #Si no se encuentra el alumno, se devuelve error
    if not resultado:
        raise HTTPException(status_code=400, detail=f"No se encontró información para el alumno con código {id}")
    
    return JSONResponse(status_code=200, content=jsonable_encoder(resultado))

@alumnoRouter.get("/{id}/media")
def get_media(id:str, request: Request):
    pool = request.app.state.pool
    df = request.app.state.df
    pdf_info = request.app.state.pdf_info
    with pool.acquire() as conn:
        with conn.cursor() as cur:
            media = funciones.calcular_media_ponderada(cur, id, "2024-25")[0]
    if media is None:
        media = funciones.calcular_media_ponderada_df(df, pdf_info, id)[0]
        print(f'Media calculada desde el DataFrame: {media}')
    if media is None or math.isnan(media):
        raise HTTPException(status_code=400, detail=f'No se ha podido calcular la media de {id}')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(media))

@alumnoRouter.get("/probabilidadEntrada/{alumnoId}/{asignatura}")
def get_probabilidad_acceso(alumnoId: str, asignatura: str, request: Request):
    pool = request.app.state.pool
    df = request.app.state.df
    pdf_info = request.app.state.pdf_info
    with pool.acquire() as conn:
        cur = conn.cursor()
        probabilidad = funciones.calcular_probabilidad_entrada(cur, asignatura, alumnoId, df, pdf_info)
    if probabilidad is None:
        raise HTTPException(status_code=400, detail=f"No se ha encontrado la probabilidad de acceso para el alumno {alumnoId} a la asignatura {asignatura}")
    return JSONResponse(status_code=200, content=jsonable_encoder(probabilidad))

@alumnoRouter.get("/afinidad/{alumnoId}/{asignatura}", tags=['Afinidad'])
def get_afinidad(alumnoId: str, asignatura: str, request: Request):
    df = request.app.state.df
    modelo, scaler, matriz, df_clusters = funciones.entrenar_clustering(df)
    afinidad = funciones.predecir_afinidad_cluster(alumnoId, asignatura, modelo, scaler, matriz, df_clusters, df)
    if (afinidad is None):
        return(JSONResponse(status_code=400, detail="No se ha encontrado al alumno"))
    return JSONResponse(status_code=200, content=jsonable_encoder(afinidad))

@alumnoRouter.post("/{id}/subir-informe")
async def procesar_pdf(id: str, request: Request ,file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf') and not file.filename.startswith('ListadoConsultaExpedienteAcademico'):
        raise HTTPException(status_code=400, detail="El archivo no es un PDF válido. No modificar el nombre del archivo tras descargar.")
    pool = request.app.state.pool
    df = request.app.state.df
    pdf_info = request.app.state.pdf_info
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