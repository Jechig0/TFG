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
from models.VerificarAlumnoPayload import VerificarAlumnoPayload

#Creamos el router para las rutas de alumnos, colocando el prefijo "/alumno" para todas las rutas
alumnoRouter = APIRouter(prefix="/alumno", tags=["Alumno"])

@alumnoRouter.get("/{id}")
def get_alumno_by_id(id:str, request: Request):
    pool: oracledb.ConnectionPool = request.app.state.pool
    #La subconsulta, que se reutiliza en el codigo, agrupa todas las notas de la base de datos de los alumnos y las asignaturas, y devuelve solo la más alta
    with pool.acquire() as conn:
        resultado = funciones.obtener_informe_alumno(conn, id)
    #Si no se encuentra el alumno, se devuelve error
    if not resultado or len(resultado) == 0:
        raise HTTPException(status_code=400, detail=f"No se encontró información para el alumno con código {id}")
    
    return JSONResponse(status_code=200, content=jsonable_encoder(resultado))

@alumnoRouter.get("/{id}/media")
def get_media(id:str, request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        with conn.cursor() as cur:
            media = funciones.calcular_media_ponderada_alumno(cur, id)[0]
    #En caso de que estemos probando un alumno de la vista en lugar de un alumno que este consultando.
            if media is None:
                media = funciones.calcular_media_ponderada_vista(cur, id, "2024-25")[0]
    if media is None or math.isnan(media):
        raise HTTPException(status_code=400, detail=f'No se ha podido calcular la media de {id}')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(media))

@alumnoRouter.get("/probabilidadEntrada/{alumnoId}/{asignatura}")
def get_probabilidad_acceso(alumnoId: str, asignatura: str, request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        cur = conn.cursor()
        probabilidad = funciones.calcular_probabilidad_entrada(cur, asignatura, alumnoId)
        if probabilidad is None:
            raise HTTPException(status_code=400, detail=f"No se ha encontrado la probabilidad de acceso para el alumno {alumnoId} a la asignatura {asignatura}")
        asignatura_estandar = funciones.obtener_asignatura_sin_normalizar(conn, asignatura)
        funciones.insertar_probabilidad_alumno(conn, alumnoId, asignatura_estandar, probabilidad)
        cur.close()

    return JSONResponse(status_code=200, content=jsonable_encoder(probabilidad))

@alumnoRouter.get("/afinidad/{alumnoId}/{asignatura}", tags=['Afinidad'])
def get_afinidad(alumnoId: str, asignatura: str, request: Request):
    pool = request.app.state.pool
    df = request.app.state.df
    with pool.acquire() as conn:
        df_ampliado = funciones.agregar_alumno_df(df, alumnoId, conn)
    modelo, scaler, matriz, df_clusters = funciones.entrenar_clustering(df_ampliado)
    afinidad = funciones.predecir_afinidad_cluster(alumnoId, asignatura, modelo, scaler, matriz, df_clusters, df_ampliado)
    if (afinidad is None):
        raise HTTPException(status_code=400, detail="No se ha encontrado al alumno")
    with pool.acquire() as conn:
        asignatura_estandar = funciones.obtener_asignatura_sin_normalizar(conn, asignatura) 
        funciones.insertar_afinidad_alumno(conn, alumnoId, asignatura_estandar, afinidad)
    return JSONResponse(status_code=200, content=jsonable_encoder(afinidad))

@alumnoRouter.post("/verificar")
def verificar_alumno(payload: VerificarAlumnoPayload, request:Request):
    id_alumno = payload.id_alumno
    dni = payload.dni
    if not id_alumno or not dni:
        raise HTTPException(status_code=400, detail="ID y DNI son obligatorios")
    pool = request.app.state.pool
    with pool.acquire() as conn:
        try:
            existe = funciones.verificar_alumno(conn, id_alumno, dni)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")

    return JSONResponse(status_code=200, content=jsonable_encoder({"existe": existe}))

@alumnoRouter.post("/{id}/subir-informe")
async def procesar_pdf(id: str, request: Request ,file: UploadFile = File(...)):
    funciones.validar_pdf(file)
    pool = request.app.state.pool
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(await file.read())
        temp_pdf_path = temp_pdf.name
    with pool.acquire() as conn:
        tablas_finales = funciones.procesar_pdf(conn, temp_pdf_path, id=id, dni='0860B')
        # Borramos el informe anterior del alumno si existe para evitar duplicados, considerando que
        # si se sube un nuevo informe, tendrá información actualizada.
        funciones.borrar_informe_alumno(conn, id)
        funciones.insertar_informe_alumno(conn, id, tablas_finales)
        resultado = funciones.obtener_informe_alumno(conn, id)
    
    os.remove(temp_pdf_path)
    if resultado is None or len(resultado) == 0:
        raise HTTPException(status_code=400, detail={"No se encontraron asignaturas con notas en el PDF proporcionado."})
    
    return JSONResponse(status_code=201, content=jsonable_encoder(resultado))

@alumnoRouter.delete("/delete/{id}")
def borrar_alumno(id: str, request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        funciones.borrar_informe_alumno(conn, id)
    
    return JSONResponse(status_code=200, content={"message": f"Alumno con ID {id} borrado exitosamente."})