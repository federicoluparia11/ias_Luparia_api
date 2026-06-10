"""Validaciones de datos de entrada (logica pura, testeable en unitarios)."""
import re

EMAIL_REGEX = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[\w\.\-]+$")


def validar_email(email):
    """Devuelve True si el email tiene formato valido."""
    if not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def validar_nombre(nombre):
    """Devuelve True si el nombre es un string no vacio de hasta 100 chars."""
    if not isinstance(nombre, str):
        return False
    nombre = nombre.strip()
    return 0 < len(nombre) <= 100


def validar_payload_usuario(payload):
    """Valida el payload completo de creacion/edicion de usuario.

    Devuelve (es_valido, mensaje_de_error).
    """
    if not isinstance(payload, dict):
        return False, "El cuerpo de la solicitud debe ser JSON"
    if not validar_nombre(payload.get("nombre")):
        return False, "El campo 'nombre' es obligatorio (max 100 caracteres)"
    if not validar_email(payload.get("email")):
        return False, "El campo 'email' es obligatorio y debe ser valido"
    return True, None
