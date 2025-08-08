from fastapi import APIRouter, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import funciones as funciones


adminRouter = APIRouter(prefix="/admin", tags=["Admin"])


@adminRouter.post('/check')
def check_admin(request: Request, payload: dict):
    user = payload.get("user")
    password = payload.get("password")
    pool = request.app.state.pool
    if not user or not password:
        raise HTTPException(status_code=400, detail="No se han proporcionado las credenciales necesarias")
    
    with pool.acquire() as conn:
        resultado = funciones.check_admin(conn, user, password)
        if resultado == 0:
            raise HTTPException(status_code=403, detail="Usuario no autorizado")
    
    return JSONResponse(status_code=200, content={"message": "Usuario autorizado"})

@adminRouter.get('/titulaciones')
def get_titulaciones(request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        titulaciones = funciones.numero_consultas_titulaciones(conn)
    if titulaciones == []:
        raise HTTPException(status_code=400, detail='No hay consultas registradas actualmente en la base de datos.')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(titulaciones))

@adminRouter.get('/asignaturas_populares')
def get_asignaturas_populares(request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        asignaturas = funciones.asignaturas_populares(conn)
    if asignaturas == []:
        raise HTTPException(status_code=400, detail='No se han encontrado asignaturas populares.')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(asignaturas))

@adminRouter.get('/asignaturas_afinidad')
def get_asignaturas_afinidad(request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        asignaturas = funciones.asignaturas_afinidad(conn)
    if asignaturas == []:
        raise HTTPException(status_code=400, detail='No se han encontrado asignaturas con afinidad.')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(asignaturas))

@adminRouter.get('/asignaturas_probabilidad')
def get_asignaturas_probabilidad(request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        asignaturas = funciones.asignaturas_probabilidad(conn)
    if asignaturas == []:
        raise HTTPException(status_code=400, detail='No se han encontrado asignaturas con probabilidad de acceso.')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(asignaturas))

@adminRouter.get("/seed")
def reiniciar_database(request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        seed = funciones.reiniciar_admin_db(conn)
    if seed is False:
        raise HTTPException(status_code=400, detail="Error al borrar la base de datos")
    return JSONResponse(status_code=200, content="SEED EXECUTED")