import io
import os
import pytest
from fastapi import UploadFile, Form
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    from unittest.mock import MagicMock
    app.state.pool = MagicMock()  # pool simulado
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

def test_subir_informe_success(monkeypatch, client):
    # Mock funciones usadas en el endpoint
    monkeypatch.setattr("app.funciones.validar_pdf", lambda file: True)
    monkeypatch.setattr("app.funciones.procesar_pdf", lambda conn, path, id, dni: {"asig": [10]})
    monkeypatch.setattr("app.funciones.borrar_informe_alumno", lambda conn, id: None)
    monkeypatch.setattr("app.funciones.insertar_informe_alumno", lambda conn, id, tablas: None)
    monkeypatch.setattr("app.funciones.obtener_informe_alumno", lambda conn, id: {"asig": [10]})

    pdf_bytes = io.BytesIO(b"%PDF-1.4 test pdf content")
    files = {"file": ("test.pdf", pdf_bytes, "application/pdf")}
    data = {"dni": "12345678A"}

    r = client.post("/alumno/123/subir-informe", files=files, data=data)
    assert r.status_code == 201
    assert r.json() == {"asig": [10]}

def test_subir_informe_sin_resultado(monkeypatch, client):
    monkeypatch.setattr("app.funciones.validar_pdf", lambda file: True)
    monkeypatch.setattr("app.funciones.procesar_pdf", lambda conn, path, id, dni: {"asig": [10]})
    monkeypatch.setattr("app.funciones.borrar_informe_alumno", lambda conn, id: None)
    monkeypatch.setattr("app.funciones.insertar_informe_alumno", lambda conn, id, tablas: None)
    monkeypatch.setattr("app.funciones.obtener_informe_alumno", lambda conn, id: None)  # No devuelve nada

    pdf_bytes = io.BytesIO(b"%PDF-1.4 test pdf content")
    files = {"file": ("test.pdf", pdf_bytes, "application/pdf")}
    data = {"dni": "12345678A"}

    r = client.post("/alumno/123/subir-informe", files=files, data=data)
    assert r.status_code == 400
    assert "No se encontraron asignaturas" in r.json()["detail"]

def test_subir_informe_sin_dni(monkeypatch, client):
    pdf_bytes = io.BytesIO(b"%PDF-1.4 test pdf content")
    files = {"file": ("test.pdf", pdf_bytes, "application/pdf")}
    data = {"dni": ""}  # DNI vacío

    r = client.post("/alumno/123/subir-informe", files=files, data=data)
    assert r.status_code == 400
    assert "DNI es obligatorio" in r.json()["detail"]
