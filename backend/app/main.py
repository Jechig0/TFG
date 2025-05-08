# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from calculo_acceso import calcular_media_ponderada
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o limita según tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de entrada
class AlumnoRequest(BaseModel):
    codigo_alumno: str

@app.post("/procesar_alumno/")
def procesar_alumno(data: AlumnoRequest):
    codigo = data.codigo_alumno

    # Aquí llamas a tus funciones personalizadas:
    resultado = calcular_media_ponderada(codigo)  # <- función que hayas definido

    return {"codigo_alumno": codigo, "media_ponderada": resultado}