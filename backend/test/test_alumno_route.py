from app import funciones
from app.main import app 
from pandas import DataFrame

def _find_path_for_endpoint(app, endpoint_name: str) -> str:
    """
    Busca en app.routes la ruta cuyo endpoint tenga el nombre dado.
    Devuelve la ruta con {id} para sustituir después.
    """
    for r in app.routes:
        # r.endpoint es la función que maneja la ruta
        if getattr(r.endpoint, "__name__", "") == endpoint_name:
            return r.path
    raise RuntimeError(f"Ruta para endpoint {endpoint_name} no encontrada en app.routes")

def test_get_alumno_success(monkeypatch, test_client):
    # preparar el retorno simulado de funciones.obtener_informe_alumno
    fake_result = [{"codigo": "123", "nombre": "Juan Pérez", "notas": [{"asig": "Matemáticas", "nota": 9.5}]}]

    monkeypatch.setattr(funciones, "obtener_informe_alumno", lambda conn, id: fake_result)

    path_template = _find_path_for_endpoint(app, "get_alumno_by_id")  # obtiene algo como "/alumno/{id}"
    path = path_template.replace("{id}", "123")

    r = test_client.get(path)
    assert r.status_code == 200
    # FastAPI devuelve JSONResponse con jsonable_encoder(resultado)
    assert r.json() == fake_result

def test_get_alumno_not_found(monkeypatch, test_client):
    # Simular que no hay información
    monkeypatch.setattr(funciones, "obtener_informe_alumno", lambda conn, id: [])
    path_template = _find_path_for_endpoint(app, "get_alumno_by_id")
    path = path_template.replace("{id}", "noexiste")

    r = test_client.get(path)
    assert r.status_code == 400
    body = r.json()
    assert "No se encontró información" in body["detail"] or "No se encontró" in str(body)

def test_get_alumno_db_error(monkeypatch, test_client):
    # Simula excepción en la capa de datos
    def raise_exc(conn, id):
        raise RuntimeError("BD falló")
    monkeypatch.setattr(funciones, "obtener_informe_alumno", raise_exc)

    path_template = _find_path_for_endpoint(app, "get_alumno_by_id")
    path = path_template.replace("{id}", "123")

    r = test_client.get(path)

    # Aserción básica del código HTTP
    assert r.status_code == 500

    # Si la app devuelve JSON, comprobaremos el detalle; si no, comprobamos el texto
    ctype = r.headers.get("content-type", "")
    if "application/json" in ctype:
        body = r.json()
        # dependiendo de tu handler de errores, puede ser {"detail": "BD falló"} o similar
        assert "BD falló" in (body.get("detail", "") or str(body))
    else:
        # body no JSON (p. ej. "Internal Server Error" o HTML)
        assert "Internal Server Error" in (r.text or "") or "BD falló" in (r.text or "")

def test_get_media_success(monkeypatch, client):
    # mock calcular_media_ponderada_alumno y calcular_media_ponderada_vista
    monkeypatch.setattr("app.funciones.calcular_media_ponderada_alumno", lambda cur, id: [8.5])
    monkeypatch.setattr("app.funciones.calcular_media_ponderada_vista", lambda cur, id, anio: [None])
    
    path = "/alumno/123/media"
    r = client.get(path)
    assert r.status_code == 200
    assert r.json() == 8.5

def test_get_media_error(monkeypatch, client):
    # devuelve None para ambos métodos → error 400
    monkeypatch.setattr("app.funciones.calcular_media_ponderada_alumno", lambda cur, id: [None])
    monkeypatch.setattr("app.funciones.calcular_media_ponderada_vista", lambda cur, id, anio: [None])
    
    path = "/alumno/123/media"
    r = client.get(path)
    assert r.status_code == 400

def test_get_probabilidad_acceso_success(monkeypatch, client):
    monkeypatch.setattr("app.funciones.calcular_probabilidad_entrada", lambda cur, asig, id: 0.75)
    monkeypatch.setattr("app.funciones.obtener_asignatura_sin_normalizar", lambda conn, asig: "ASIG_STD")
    monkeypatch.setattr("app.funciones.insertar_probabilidad_alumno", lambda conn, id, asig, prob: None)
    
    path = "/alumno/probabilidadEntrada/123/Mates"
    r = client.get(path)
    assert r.status_code == 200
    assert r.json() == 0.75

def test_get_probabilidad_acceso_not_found(monkeypatch, client):
    monkeypatch.setattr("app.funciones.calcular_probabilidad_entrada", lambda cur, asig, id: None)
    path = "/alumno/probabilidadEntrada/123/Mates"
    r = client.get(path)
    assert r.status_code == 400

def test_get_afinidad_success(monkeypatch, client):
    # mocks para obtener_vector_alumno y predecir_afinidad_cluster
    from pandas import DataFrame
    monkeypatch.setattr("app.funciones.obtener_vector_alumno", lambda conn, id, cols: DataFrame([{"a":1}]))
    monkeypatch.setattr("app.funciones.predecir_afinidad_cluster", lambda **kwargs: 0.95)
    monkeypatch.setattr("app.funciones.obtener_asignatura_sin_normalizar", lambda conn, asig: "ASIG_STD")
    monkeypatch.setattr("app.funciones.insertar_afinidad_alumno", lambda conn, id, asig, afinidad: None)

    path = "/alumno/afinidad/123/Mates"
    r = client.get(path)
    assert r.status_code == 200
    assert r.json() == 0.95

def test_get_afinidad_no_notas(monkeypatch, client):
    from pandas import DataFrame
    monkeypatch.setattr("app.funciones.obtener_vector_alumno", lambda conn, id, cols: DataFrame())
    path = "/alumno/afinidad/123/Mates"
    r = client.get(path)
    assert r.status_code == 400

def test_get_afinidad_asignatura_no_vista(monkeypatch, client):

    # alumno_row no vacío → pasa la primera excepción
    monkeypatch.setattr("app.funciones.obtener_vector_alumno", lambda conn, id, cols: DataFrame([{"a":1}]))
    # predecir_afinidad_cluster devuelve None → dispara excepción de asignatura no vista
    monkeypatch.setattr("app.funciones.predecir_afinidad_cluster", lambda **kwargs: None)

    path = "/alumno/afinidad/123/Mates"
    r = client.get(path)
    assert r.status_code == 400
    assert "Asignatura no vista" in r.json()["detail"]


def test_verificar_alumno_nuevo(monkeypatch, client):
    monkeypatch.setattr("app.funciones.existe_alumno", lambda conn, id, dni: None)
    payload = {"id_alumno": "123", "dni": "12345678A"}
    r = client.post("/alumno/verificar", json=payload)
    assert r.status_code == 200
    assert r.json()["estado"] == "nuevo"

def test_verificar_alumno_dni_incorrecto(monkeypatch, client):
    monkeypatch.setattr("app.funciones.existe_alumno", lambda conn, id, dni: True)
    monkeypatch.setattr("app.funciones.verificar_alumno", lambda conn, id, dni: False)
    payload = {"id_alumno": "123", "dni": "00000000A"}
    r = client.post("/alumno/verificar", json=payload)
    assert r.status_code == 400
    assert r.json()["estado"] == "dni_incorrecto"

def test_verificar_alumno_existente(monkeypatch, client):
    monkeypatch.setattr("app.funciones.existe_alumno", lambda conn, id, dni: True)
    monkeypatch.setattr("app.funciones.verificar_alumno", lambda conn, id, dni: True)
    payload = {"id_alumno": "123", "dni": "12345678A"}
    r = client.post("/alumno/verificar", json=payload)
    assert r.status_code == 200
    assert r.json()["estado"] == "existente"

def test_verificar_alumno_campos_vacios(client):
    payload = {"id_alumno": "", "dni": "12345678A"}  # ID vacío
    r = client.post("/alumno/verificar", json=payload)
    assert r.status_code == 400
    assert "obligatorios" in r.json()["detail"]

    payload = {"id_alumno": "123", "dni": ""}  # DNI vacío
    r = client.post("/alumno/verificar", json=payload)
    assert r.status_code == 400
    assert "obligatorios" in r.json()["detail"]


def test_borrar_alumno(monkeypatch, client):
    monkeypatch.setattr("app.funciones.borrar_informe_alumno", lambda conn, id: None)
    monkeypatch.setattr("app.funciones.borrar_alumno_verificado", lambda conn, id: None)
    r = client.delete("/alumno/delete/123")
    assert r.status_code == 200
    assert "123" in r.json()["message"]
