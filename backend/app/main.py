# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir acceso desde Angular (ajusta el dominio según el entorno)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # dominio de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de entrada
class DatosEntrada(BaseModel):
    codigo_alumno: str
    asignatura: str