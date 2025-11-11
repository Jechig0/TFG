from pydantic import BaseModel

class PonderacionPayload(BaseModel):
    year: str
    peso: float