import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock

# --- Fixtures ---
@pytest.fixture(scope="module")
def client():
    app.state.pool = MagicMock()
    app.state.df = MagicMock()
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

# --- Tests ---

def test_check_admin_success(monkeypatch, client):
    monkeypatch.setattr("app.funciones.check_admin", lambda conn, user, pw: 1)
    payload = {"user": "admin", "password": "1234"}
    r = client.post("/admin/check", json=payload)
    assert r.status_code == 200
    assert r.json() == {"message": "Usuario autorizado"}

def test_check_admin_missing_credentials(client):
    payload = {"user": "", "password": ""}
    r = client.post("/admin/check", json=payload)
    assert r.status_code == 400
    assert "credenciales" in r.json()["detail"]

def test_check_admin_unauthorized(monkeypatch, client):
    monkeypatch.setattr("app.funciones.check_admin", lambda conn, user, pw: 0)
    payload = {"user": "admin", "password": "1234"}
    r = client.post("/admin/check", json=payload)
    assert r.status_code == 403
    assert "no autorizado" in r.json()["detail"]

def test_get_titulaciones(monkeypatch, client):
    monkeypatch.setattr("app.funciones.numero_consultas_titulaciones", lambda conn: ["Titulacion1"])
    r = client.get("/admin/titulaciones")
    assert r.status_code == 200
    assert r.json() == ["Titulacion1"]

def test_get_asignaturas_populares(monkeypatch, client):
    monkeypatch.setattr("app.funciones.asignaturas_populares", lambda conn: ["Asig1", "Asig2"])
    r = client.get("/admin/asignaturas_populares")
    assert r.status_code == 200
    assert r.json() == ["Asig1", "Asig2"]

def test_get_asignaturas_afinidad(monkeypatch, client):
    monkeypatch.setattr("app.funciones.asignaturas_afinidad", lambda conn: ["AsigA"])
    r = client.get("/admin/asignaturas_afinidad")
    assert r.status_code == 200
    assert r.json() == ["AsigA"]

def test_get_asignaturas_probabilidad(monkeypatch, client):
    monkeypatch.setattr("app.funciones.asignaturas_probabilidad", lambda conn: ["AsigP"])
    r = client.get("/admin/asignaturas_probabilidad")
    assert r.status_code == 200
    assert r.json() == ["AsigP"]

def test_reiniciar_clusters_success(monkeypatch, client):
    monkeypatch.setattr("app.funciones.reiniciar_clusters", lambda conn, req: True)
    r = client.post("/admin/reiniciar_clusters")
    assert r.status_code == 200
    assert r.json() == {"message": "Clusters reiniciados correctamente"}

def test_reiniciar_clusters_fail(monkeypatch, client):
    monkeypatch.setattr("app.funciones.reiniciar_clusters", lambda conn, req: False)
    r = client.post("/admin/reiniciar_clusters")
    assert r.status_code == 400
    assert "Error al reiniciar" in r.json()["detail"]

def test_get_ponderaciones_success(monkeypatch, client):
    monkeypatch.setattr("app.funciones.get_ponderaciones", lambda conn: [{"year": 2024, "peso": 0.5}])
    r = client.get("/admin/get_ponderaciones")
    assert r.status_code == 200
    assert r.json() == [{"year": 2024, "peso": 0.5}]

def test_get_ponderaciones_empty(monkeypatch, client):
    monkeypatch.setattr("app.funciones.get_ponderaciones", lambda conn: [])
    r = client.get("/admin/get_ponderaciones")
    assert r.status_code == 400
    assert "años disponibles" in r.json()["detail"]

def test_set_ponderaciones_success(monkeypatch, client):
    monkeypatch.setattr("app.funciones.set_ponderaciones", lambda conn, ponderaciones: True)
    payload = {"ponderaciones": [{"year": 2024, "peso": 1.0}]}
    r = client.post("/admin/set_ponderaciones", json=payload)
    assert r.status_code == 200
    assert "Ponderaciones establecidas" in r.json()["message"]

def test_set_ponderaciones_missing_data(client):
    payload = {"ponderaciones": None}
    r = client.post("/admin/set_ponderaciones", json=payload)
    assert r.status_code == 400
    assert "datos necesarios" in r.json()["detail"]

def test_set_ponderaciones_invalid_weight(client):
    payload = {"ponderaciones": [{"year": 2024, "peso": 1.5}]}
    r = client.post("/admin/set_ponderaciones", json=payload)
    assert r.status_code == 400
    assert "Peso inválido" in r.json()["detail"]

def test_set_ponderaciones_sum_exceeds(client):
    payload = {"ponderaciones": [{"year": 2024, "peso": 0.6}, {"year": 2025, "peso": 0.5}]}
    r = client.post("/admin/set_ponderaciones", json=payload)
    assert r.status_code == 400
    assert "suma de pesos" in r.json()["detail"]

def test_set_ponderaciones_fail(monkeypatch, client):
    monkeypatch.setattr("app.funciones.set_ponderaciones", lambda conn, ponderaciones: False)
    payload = {"ponderaciones": [{"year": 2024, "peso": 1.0}]}
    r = client.post("/admin/set_ponderaciones", json=payload)
    assert r.status_code == 400
    assert "Error al establecer" in r.json()["detail"]

def test_reset_consultas_success(monkeypatch, client):
    monkeypatch.setattr("app.funciones.borrar_consultas", lambda conn: True)
    r = client.post("/admin/reset_consultas")
    assert r.status_code == 200
    assert r.text == '"Consultas borradas correctamente"'

def test_reset_consultas_fail(monkeypatch, client):
    monkeypatch.setattr("app.funciones.borrar_consultas", lambda conn: False)
    r = client.post("/admin/reset_consultas")
    assert r.status_code == 400
    assert "Error al borrar" in r.json()["detail"]

def test_reset_expedientes_success(monkeypatch, client):
    monkeypatch.setattr("app.funciones.borrar_expedientes", lambda conn: True)
    r = client.post("/admin/reset_expedientes")
    assert r.status_code == 200
    assert r.text == '"SEED EXECUTED"'

def test_reset_expedientes_fail(monkeypatch, client):
    monkeypatch.setattr("app.funciones.borrar_expedientes", lambda conn: False)
    r = client.post("/admin/reset_expedientes")
    assert r.status_code == 400
    assert "Error al borrar" in r.json()["detail"]
