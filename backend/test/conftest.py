import pytest
from fastapi.testclient import TestClient
from app.main import app  # ajusta import según tu proyecto

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
# Fake connection / pool que replica el comportamiento 'with pool.acquire() as conn:'
class FakeConn:
    def __init__(self, payload=None):
        self.payload = payload

class FakeAcquire:
    def __init__(self, conn):
        self.conn = conn
    def __enter__(self):
        return self.conn
    def __exit__(self, exc_type, exc, tb):
        return False  # no suprimir excepciones

class FakePool:
    def __init__(self, conn=None):
        self._conn = conn or FakeConn()
    def acquire(self):
        return FakeAcquire(self._conn)

@pytest.fixture(scope="session")
def test_client():
    # inyecta el pool falso en app.state
    app.state.pool = FakePool()
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client

