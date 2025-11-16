import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.routers.asignatura import asignaturaRouter
from fastapi import FastAPI

# Creamos una app de test con el router incluido
app = FastAPI()
app.include_router(asignaturaRouter)

# Mock de pool y conexión
class MockCursor:
    def fetchall(self):
        return []

class MockConnection:
    def cursor(self):
        return MockCursor()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        pass

class MockPool:
    def acquire(self):
        return MockConnection()
    def __enter__(self):
        return self.acquire()
    def __exit__(self, exc_type, exc_value, traceback):
        pass

@pytest.fixture
def test_client():
    # Añadimos la pool simulada a la app
    app.state.pool = MockPool()
    client = TestClient(app)
    return client

def test_get_asignatura_success(monkeypatch, test_client):
    # Mock de la función para devolver datos de prueba
    def mock_obtener_optativas_por_titulacion(id, conn):
        return [("Matemáticas",), ("Física",)]
    monkeypatch.setattr("app.funciones.obtener_optativas_por_titulacion", mock_obtener_optativas_por_titulacion)
    
    response = test_client.get("/asignatura/2023ABC")
    assert response.status_code == 200
    assert response.json() == [["Matemáticas"], ["Física"]]

def test_get_asignatura_no_results(monkeypatch, test_client):
    # Mock de la función para devolver lista vacía
    def mock_obtener_optativas_por_titulacion(id, conn):
        return []
    monkeypatch.setattr("app.funciones.obtener_optativas_por_titulacion", mock_obtener_optativas_por_titulacion)
    
    response = test_client.get("/asignatura/2023XYZ")
    assert response.status_code == 400
    assert "No se han encontrado asignaturas" in response.json()["detail"]
