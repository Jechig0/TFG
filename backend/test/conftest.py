import pytest
from fastapi.testclient import TestClient
from app.main import app  # ajusta import según tu proyecto
import tipos_dummy as td  # opcional: helpers

@pytest.fixture
def client():
    # Puedes preparar aquí app.state.pool con un fake pool si tus endpoints lo usan
    return TestClient(app)

# Fixture para funciones puras si necesitas un ejemplo de tabla
@pytest.fixture
def ejemplo_tabla():
    return [
        ['Denominación asignatura', 'Créditos', 'Curso Acad.', 'Convocatoria', 'Calif.Num.', 'Calif.Literal'],
        ['Procesadores de Lenguajes', '6', '2022/23', 'ENE/2023', '', 'No presentado'],
        [None, '6', '2022/23', 'SEP/2023', '2.60', 'Suspenso'],
    ]
