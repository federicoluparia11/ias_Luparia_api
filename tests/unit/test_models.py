"""Tests unitarios: serializacion del modelo Usuario."""
from app.models import Usuario


def test_usuario_to_dict():
    usuario = Usuario(id=1, nombre="Ana", email="ana@mail.com")
    resultado = usuario.to_dict()
    assert resultado == {"id": 1, "nombre": "Ana", "email": "ana@mail.com"}


def test_usuario_to_dict_contiene_claves_esperadas():
    usuario = Usuario(id=7, nombre="Beto", email="beto@mail.com")
    assert set(usuario.to_dict().keys()) == {"id", "nombre", "email"}
