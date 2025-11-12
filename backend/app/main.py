#Importaciones necesarias en main.
from contextlib import asynccontextmanager
import pandas as pd
import oracledb as oracledb
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app import funciones
from fastapi.middleware.cors import CORSMiddleware
from app.routers.alumno import alumnoRouter
from app.routers.asignatura import asignaturaRouter
from app.routers.admin import adminRouter

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏳ Creando pool de conexiones...")
    dsn = oracledb.makedsn("afrodita.lcc.uma.es", 1521, sid="APOLO")
    # Crear un pool de conexiones para mejorar el rendimiento y poder atender múltiples peticiones simultáneamente
    pool = oracledb.create_pool(
        user="tfm_puertas",
        password="JCGRmlbEsc",
        dsn=dsn,
        min=1,
        max=10,
        increment=1
    )
    
    app.state.pool = pool

    # Crear conexión temporal para cargar el DataFrame
    with pool.acquire() as conn:
        df = funciones.crear_df(conn)
        df["NUM_CALIFICACIÓN"] = (
        df["NUM_CALIFICACIÓN"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )
        df["NUM_CALIFICACIÓN"] = pd.to_numeric(df["NUM_CALIFICACIÓN"], errors="coerce")

        modelo, scaler, matriz, df_clusters = funciones.entrenar_clustering(df)
        app.state.df = df
        app.state.modelo = modelo
        app.state.scaler = scaler
        app.state.matriz = matriz
        app.state.df_clusters = df_clusters

    print("✅ Pool creado correctamente")
    yield  # Espera a que la app corra
    print("🧹 Cerrando pool de conexiones...")
    pool.close()
    print("✅ Pool cerrado correctamente")

#Inicialización de la aplicación FastAPI
app = FastAPI(
    title='FastAPI', #Título que aparecerá en la documentación
    description="API Recomendador Asignaturas", #Descripción debajo del título
    version='1.0.0', #Número de la etiqueta gris al lado del título
    lifespan=lifespan #Contexto de vida de la aplicación
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
app.include_router(adminRouter)

# Redirección a la documentación de FastAPI al acceder a la raíz
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url='/docs')

@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}