from fastapi import APIRouter, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import app.funciones as funciones


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
    # if titulaciones == []:
    #     raise HTTPException(status_code=400, detail='No hay consultas registradas actualmente en la base de datos.')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(titulaciones))

@adminRouter.get('/asignaturas_populares')
def get_asignaturas_populares(request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        asignaturas = funciones.asignaturas_populares(conn)
    # if asignaturas == []:
    #     raise HTTPException(status_code=400, detail='No se han encontrado asignaturas populares.')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(asignaturas))

@adminRouter.get('/asignaturas_afinidad')
def get_asignaturas_afinidad(request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        asignaturas = funciones.asignaturas_afinidad(conn)
    # if asignaturas == []:
    #     raise HTTPException(status_code=400, detail='No se han encontrado asignaturas con afinidad.')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(asignaturas))

@adminRouter.get('/asignaturas_probabilidad')
def get_asignaturas_probabilidad(request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        asignaturas = funciones.asignaturas_probabilidad(conn)
    # if asignaturas == []:
    #     raise HTTPException(status_code=400, detail='No se han encontrado asignaturas con probabilidad de acceso.')
    
    return JSONResponse(status_code=200, content=jsonable_encoder(asignaturas))

@adminRouter.post("/reiniciar_clusters")
def reiniciar_clusters(request: Request):
    pool = request.app.state.pool
    df = request.app.state.df
    with pool.acquire() as conn:
        resultado = funciones.reiniciar_clusters(conn, request)
    if resultado is False:
        raise HTTPException(status_code=400, detail="Error al reiniciar los clusters")
    return JSONResponse(status_code=200, content={"message": "Clusters reiniciados correctamente"})

@adminRouter.get("/get_ponderaciones")
def get_años(request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        años = funciones.get_ponderaciones(conn)
    if años == []:
        raise HTTPException(status_code=400, detail="No se han encontrado años disponibles")
    return JSONResponse(status_code=200, content=jsonable_encoder(años))

@adminRouter.post("/set_ponderaciones")
def set_ponderaciones(request: Request, payload: dict):
    pool = request.app.state.pool
    ponderaciones = payload.get("ponderaciones")
    if not ponderaciones:
        raise HTTPException(status_code=400, detail="No se han proporcionado los datos necesarios")
    total = 0.0
    for item in ponderaciones:
        if item['peso'] < 0 or item['peso'] > 1:
            raise HTTPException(status_code=400, detail=f"Peso inválido para {item['year']}")
        total += float(item['peso'])

    if total > 1 + 0.000001 or total < 1 - 0.000001:  # tolerancia
        raise HTTPException(status_code=400, detail=f"La suma de pesos ({total}) excede 1")
    
    with pool.acquire() as conn:
        resultado = funciones.set_ponderaciones(conn, ponderaciones)
    if resultado is False:
        raise HTTPException(status_code=400, detail="Error al establecer las ponderaciones")
    
    return JSONResponse(status_code=200, content={"message": "Ponderaciones establecidas correctamente"})

@adminRouter.post("/reset_consultas")
def borrar_consultas(request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        seed = funciones.borrar_consultas(conn)
    if seed is False:
        raise HTTPException(status_code=400, detail="Error al borrar la base de datos")
    return JSONResponse(status_code=200, content="Consultas borradas correctamente")

@adminRouter.post("/reset_expedientes")
def borrar_expedientes(request: Request):
    pool = request.app.state.pool
    with pool.acquire() as conn:
        seed = funciones.borrar_expedientes(conn)
    if seed is False:
        raise HTTPException(status_code=400, detail="Error al borrar la base de datos")
    return JSONResponse(status_code=200, content="SEED EXECUTED")