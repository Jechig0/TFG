import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
import hashlib
from fastapi import HTTPException
import builtins

import app.funciones as funciones

# --- Fixtures ---
@pytest.fixture
def fake_cursor():
    cur = MagicMock()
    cur.fetchone.return_value = (5.0, 12, 60)
    cur.fetchall.return_value = [(5.0, 12, 60)]
    return cur

@pytest.fixture
def fake_conn(fake_cursor):
    conn = MagicMock()
    conn.cursor.return_value = fake_cursor
    return conn

# --- Tests cálculo media ponderada ---
def test_calcular_media_ponderada_vista(fake_cursor):
    result = funciones.calcular_media_ponderada_vista(fake_cursor, "A001", "2022-23")
    assert isinstance(result, tuple)
    assert result[0] is not None
    assert result[1] > 0

def test_calcular_media_ponderada_vista_sin_datos(fake_cursor):
    fake_cursor.fetchone.return_value = (None, 0, None)
    result = funciones.calcular_media_ponderada_vista(fake_cursor, "A001", "2022-23")
    assert result == (None, 0)

# --- Tests normalización de asignatura ---
def test_normalizar_asignatura():
    assert funciones.normalizar_asignatura(" Matemáticas ") == "Matemáticas"
    assert funciones.normalizar_asignatura("") == ""
    assert funciones.normalizar_asignatura(None) == ""

# --- Test calcular_media_ponderada_alumno ---
def test_calcular_media_ponderada_alumno(fake_cursor):
    result = funciones.calcular_media_ponderada_alumno(fake_cursor, "A001")
    assert isinstance(result, tuple)

# --- Test extraer_tablas ---
@patch("pdfplumber.open")
def test_extraer_tablas(mock_pdf):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Linea1\nLinea2\nLinea3\nLinea4\nLinea5\nLinea6"
    mock_page.extract_tables.return_value = [[[1,2,3]]]
    mock_pdf.return_value.__enter__.return_value.pages = [mock_page]
    
    tables, dni, id_pdf = funciones.extraer_tablas("fake.pdf")
    assert tables
    assert dni
    assert id_pdf

# --- Test rellenar_asignaturas ---
def test_rellenar_asignaturas():
    tabla = [["Asignatura1", 5], [None, 6], ["Asignatura2", 7]]
    nueva_tabla, ultima = funciones.rellenar_asignaturas(tabla)
    assert nueva_tabla[0][0] == "Asignatura1"
    assert nueva_tabla[1][0] == "Asignatura2"
    assert ultima == "Asignatura2"


# --- Test limpiar_tabla ---
def test_limpiar_tabla():
    tabla = [["A1", 5], ["", 6], [None, 7]]
    limpia, ultima = funciones.limpiar_tabla(tabla)
    assert limpia
    assert ultima == "A1"

# --- Test limpiar_tablas_finales ---
def test_limpiar_tablas_finales():
    tablas = [[[1,2,3,4], [5,6,7,8]], [[1,2,3,4]]]
    final = funciones.limpiar_tablas_finales(tablas)
    assert isinstance(final, list)

# --- Test verificar_alumno ---
def test_verificar_alumno(fake_conn):
    dni = "12345678A"
    hash_dni = hashlib.sha256(dni.strip().upper().encode()).hexdigest()
    fake_conn.cursor.return_value.fetchone.return_value = (1,)
    result = funciones.verificar_alumno(fake_conn, "A001", dni)
    assert result is True

# --- Test existe_alumno ---
def test_existe_alumno(fake_conn):
    fake_conn.cursor.return_value.fetchone.return_value = (1,)
    result = funciones.existe_alumno(fake_conn, "A001", "DNI")
    assert result == (1,)

# --- Test validar_pdf ---
class FakeFile:
    def __init__(self, filename, content_type):
        self.filename = filename
        self.content_type = content_type

def test_validar_pdf():
    file = FakeFile("ListadoConsultaExpedienteAcademico.pdf", "application/pdf")
    assert funciones.validar_pdf(file) is True
    file_wrong = FakeFile("otro.pdf", "application/pdf")
    with pytest.raises(HTTPException):
        funciones.validar_pdf(file_wrong)
    file_wrong2 = FakeFile("ListadoConsultaExpedienteAcademico.pdf", "text/plain")
    with pytest.raises(HTTPException):
        funciones.validar_pdf(file_wrong2)

# --- Test reiniciar_clusters ---
def test_reiniciar_clusters(monkeypatch, fake_conn):
    class DummyApp:
        state = type('', (), {})()
    class DummyRequest:
        app = DummyApp()
    df = pd.DataFrame({"CODIGOALUM":["A001"], "NOMBREASIGNATURA":["M1"], "NUM_CALIFICACIÓN":[5.0]})
    monkeypatch.setattr(funciones, "crear_df", lambda conn: df)
    monkeypatch.setattr(funciones, "entrenar_clustering", lambda df, n_clusters=12: (MagicMock(), MagicMock(), df, pd.DataFrame({"CODIGOALUM":["A001"], "cluster":[0]})))
    request = DummyRequest()
    result = funciones.reiniciar_clusters(fake_conn, request)
    assert result is True

# --- Test procesar_pdf ---
@patch("app.funciones.extraer_tablas")
@patch("app.funciones.guardar_alumno_verificado")
@patch("app.funciones.limpiar_tabla")
@patch("app.funciones.limpiar_tablas_finales")
def test_procesar_pdf(mock_limp_final, mock_limp_tabla, mock_guardar, mock_extraer, fake_conn):
    mock_extraer.return_value = ([[["Asignatura",5]]], " DNIEXTRA ", "IDEXTRA")
    mock_limp_tabla.side_effect = lambda t, u=None: (t, "Ultima")
    mock_limp_final.return_value = [[["Asignatura",5]]]
    
    id_pdf = "IDEXTRA"
    dni_original = "DNIEXTRA"
    
    result = funciones.procesar_pdf(fake_conn, "fake.pdf", id_pdf, dni_original)
    assert result == [[["Asignatura",5]]]


# --- Tests de inserción de afinidad y probabilidad ---
def test_insertar_afinidad_alumno(fake_conn):
    result = funciones.insertar_afinidad_alumno(fake_conn, "TITL001", "Asig", 0.5)
    assert result is True

def test_insertar_probabilidad_alumno(fake_conn):
    result = funciones.insertar_probabilidad_alumno(fake_conn, "TITL001", "Asig", 0.7)
    assert result is True

# --- Test borrar_consultas y borrar_expedientes ---
def test_borrar_consultas(fake_conn):
    result = funciones.borrar_consultas(fake_conn)
    assert result is True

def test_borrar_expedientes(fake_conn):
    result = funciones.borrar_expedientes(fake_conn)
    assert result is True
