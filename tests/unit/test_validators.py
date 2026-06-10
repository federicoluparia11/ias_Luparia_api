"""Tests unitarios: validaciones de datos (logica pura, sin DB ni HTTP)."""
from app.validators import validar_email, validar_nombre, validar_payload_usuario


class TestValidarEmail:
    def test_email_valido(self):
        assert validar_email("juan.perez@gmail.com") is True

    def test_email_con_subdominio(self):
        assert validar_email("alumno@campus.unimoron.edu.ar") is True

    def test_email_sin_arroba(self):
        assert validar_email("juanperez.gmail.com") is False

    def test_email_sin_dominio(self):
        assert validar_email("juan@") is False

    def test_email_vacio(self):
        assert validar_email("") is False

    def test_email_no_string(self):
        assert validar_email(12345) is False
        assert validar_email(None) is False


class TestValidarNombre:
    def test_nombre_valido(self):
        assert validar_nombre("Juan Perez") is True

    def test_nombre_vacio(self):
        assert validar_nombre("") is False

    def test_nombre_solo_espacios(self):
        assert validar_nombre("   ") is False

    def test_nombre_demasiado_largo(self):
        assert validar_nombre("a" * 101) is False

    def test_nombre_no_string(self):
        assert validar_nombre(None) is False
        assert validar_nombre(42) is False


class TestValidarPayload:
    def test_payload_valido(self):
        ok, error = validar_payload_usuario({"nombre": "Ana", "email": "ana@mail.com"})
        assert ok is True
        assert error is None

    def test_payload_sin_nombre(self):
        ok, error = validar_payload_usuario({"email": "ana@mail.com"})
        assert ok is False
        assert "nombre" in error

    def test_payload_sin_email(self):
        ok, error = validar_payload_usuario({"nombre": "Ana"})
        assert ok is False
        assert "email" in error

    def test_payload_no_es_dict(self):
        ok, _ = validar_payload_usuario(None)
        assert ok is False
