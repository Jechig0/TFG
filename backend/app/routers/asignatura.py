#Rutas relacionadas con asignaturas (afinidad, probabilidad de acceso, etc.)

#Añadir las importaciones necesarias
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Request
import funciones as funciones

#Creamos el router para las rutas de asignaturas, colocando el prefijo "/asignatura" para todas las rutas
asignaturaRouter = APIRouter(prefix="/asignatura", tags=["Asignatura"])

@asignaturaRouter.get("/{id}")
def get_asignatura(id:str, request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        asignaturas = funciones.obtener_optativas_por_titulacion(id, conn)
    if not asignaturas:
        raise HTTPException(status_code=400, detail='No se han encontrado asignaturas para la titulación.')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(asignaturas))