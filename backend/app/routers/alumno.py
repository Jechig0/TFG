#Rutas relacionadas con alumnos (notas, media, etc.)

#Añadir las importaciones necesarias
import math
import os
import tempfile
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.params import Form
from fastapi.responses import JSONResponse
import oracledb
import pandas as pd
import app.funciones as funciones
from app.models.VerificarAlumnoPayload import VerificarAlumnoPayload

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
    # Objetos ya cargados en startup
    modelo = request.app.state.modelo
    scaler = request.app.state.scaler
    matriz = request.app.state.matriz         # matriz (pivot) del entreno
    df_clusters = request.app.state.df_clusters
    df_original = request.app.state.df        # df "largo" del entreno (CODIGOALUM, NOMBREASIGNATURA, NUM_CALIFICACIÓN)

    # 1) Vector 1×N del alumno con columnas=matriz.columns
    pool = request.app.state.pool
    with pool.acquire() as conn:
        alumno_row = funciones.obtener_vector_alumno(conn, alumnoId, list(matriz.columns))

    if alumno_row.empty:
        # No hay notas del alumno en informes_alumno
        raise HTTPException(status_code=400, detail="No se encontraron notas para el alumno")

    # 2) Calcular afinidad usando el modelo existente + vector del alumno
    afinidad = funciones.predecir_afinidad_cluster(
        alumno_id=alumnoId,
        asignatura=asignatura,
        modelo=modelo,
        scaler=scaler,
        matriz_base=matriz,
        df_clusters=df_clusters,
        df_original=df_original,
        alumno_row=alumno_row,      # ← importante
    )

    if afinidad is None:
        raise HTTPException(status_code=400, detail="Asignatura no vista en el entrenamiento o datos insuficientes")

    # 3) (Opcional) Guardar en ADMIN_INFO con el nombre original de la asignatura
    with pool.acquire() as conn:
        asignatura_estandar = funciones.obtener_asignatura_sin_normalizar(conn, asignatura)
        funciones.insertar_afinidad_alumno(conn, alumnoId, asignatura_estandar, afinidad)

    return JSONResponse(status_code=200, content=jsonable_encoder(afinidad))

@alumnoRouter.post("/verificar")
def verificar_alumno(payload: VerificarAlumnoPayload, request: Request):
    id_alumno = payload.id_alumno.strip()
    dni = payload.dni.strip()
    
    if not id_alumno or not dni:
        raise HTTPException(status_code=400, detail="ID y DNI son obligatorios")

    pool = request.app.state.pool
    with pool.acquire() as conn:
        # 1. Comprobar si el alumno está en ALUMNOS_VERIFICADOS
        fila = funciones.existe_alumno(conn, id_alumno, dni)

        if not fila:
            return JSONResponse(status_code=200, content={"estado": "nuevo"})  # No está registrado aún

        valido = funciones.verificar_alumno(conn, id_alumno, dni)

        if not valido:
            return JSONResponse(status_code=400, content={"estado": "dni_incorrecto"})  # Está registrado pero el DNI no coincide

        # 2. Comprobar si tiene notas en informes_alumno
        return JSONResponse(status_code=200, content={"estado": "existente"})  # Tiene notas y el DNI es correcto


@alumnoRouter.post("/{id}/subir-informe") #TODO: Error con el insertar_informe_alumno al cambiarlo a MERGE. Cambio para que no se borre de alumnos_verificados
async def procesar_pdf(
    id: str,
    request: Request,
    file: UploadFile = File(...),
    dni: str = Form(...)
):
    if not dni:
        raise HTTPException(status_code=400, detail="El DNI es obligatorio.")
    
    funciones.validar_pdf(file)
    pool = request.app.state.pool

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(await file.read())
        temp_pdf_path = temp_pdf.name

    with pool.acquire() as conn:
        tablas_finales = funciones.procesar_pdf(conn, temp_pdf_path, id=id, dni=dni)
        funciones.borrar_informe_alumno(conn, id)
        funciones.insertar_informe_alumno(conn, id, tablas_finales)
        resultado = funciones.obtener_informe_alumno(conn, id)

    os.remove(temp_pdf_path)

    if not resultado:
        raise HTTPException(status_code=400, detail="No se encontraron asignaturas con notas en el PDF.")

    return JSONResponse(status_code=201, content=jsonable_encoder(resultado))


@alumnoRouter.delete("/delete/{id}")
def borrar_alumno(id: str, request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        funciones.borrar_informe_alumno(conn, id)
        funciones.borrar_alumno_verificado(conn, id)
    
    return JSONResponse(status_code=200, content={"message": f"Alumno con ID {id} borrado exitosamente."})