from pydantic import BaseModel

class VerificarAlumnoPayload(BaseModel):
    id_alumno: str
    dni: str