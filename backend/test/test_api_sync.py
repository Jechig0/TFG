from fastapi.testclient import TestClient
from app.main import app

def test_root_redirects(client: TestClient):
    r = client.get("/")
    assert r.status_code in (200, 307, 302)  # según tu implementación

def test_verificar_alumno_mockado(client, monkeypatch):
    # Mockear la función verificar_alumno para que devuelva True
    def fake_verificar(conn, id_alumno, dni):
        return True

    monkeypatch.setattr("app.funciones.verificar_alumno", fake_verificar)

    payload = {"id_alumno": "104101657", "dni": "0860B"}
    resp = client.post("/alumno/verificar", json=payload)
    assert resp.status_code == 200
    assert resp.json().get("existe") == True
