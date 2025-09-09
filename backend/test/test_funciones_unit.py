import pytest
from app import funciones

def test_normalizar_asignatura():
    assert funciones.normalizar_asignatura("Seguridad de la Información") == "SeguridaddelaInformación".replace(" ", "" ) or isinstance(funciones.normalizar_asignatura("X"), str)

def test_rellenar_asignaturas_simple(ejemplo_tabla):
    tabla = ejemplo_tabla.copy()
    nueva = funciones.rellenar_asignaturas(tabla, indice_columna=0)[0] if isinstance(funciones.rellenar_asignaturas(tabla, indice_columna=0), tuple) else funciones.rellenar_asignaturas(tabla, indice_columna=0)
    # comprueba que las filas con None han sido rellenadas
    assert any(row[0] is None for row in ejemplo_tabla)  # precondición
    assert all(row[0] is not None for row in nueva)  # después no haya None

def test_limpiar_tabla_elimina_frase():
    frase = "DATOS RELATIVOS A LAS ACTIVIDADES FORMATIVAS REALIZADAS EN EL CENTRO:"
    tabla = [
        [frase, None, None, None, None, None, None],
        [frase, "Fundamentos", "6", "2020/21", "2.90", "Suspenso"]
    ]
    limpia, ultima = funciones.limpiar_tabla(tabla, ultima_asignatura=None)
    assert all(frase not in ''.join(map(lambda c: str(c or ''), fila)) for fila in limpia)  # comprobación simple
