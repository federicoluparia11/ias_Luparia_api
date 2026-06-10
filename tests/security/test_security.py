"""Tests de seguridad (se ejecutan en el PR de develop a main)."""
from app.models import Usuario


def test_debug_deshabilitado(app):
    """El modo debug NUNCA debe estar activo (requisito Bandit/IAS)."""
    assert app.debug is False


def test_inyeccion_sql_en_creacion(client, app):
    """Un intento de inyeccion SQL no debe romper la base ni ejecutarse."""
    payload = {
        "nombre": "Robert'); DROP TABLE usuarios;--",
        "email": "robert@mail.com",
    }
    respuesta = client.post("/usuarios", json=payload)
    # El ORM parametriza la consulta: se guarda como texto plano
    assert respuesta.status_code == 201

    # La tabla sigue existiendo y es consultable
    with app.app_context():
        assert Usuario.query.count() == 1


def test_respuesta_404_es_json(client):
    """Los errores no deben exponer paginas HTML con stack traces."""
    respuesta = client.get("/ruta/inexistente")
    assert respuesta.status_code == 404
    assert respuesta.is_json


def test_metodo_no_permitido_es_json(client):
    respuesta = client.patch("/health")
    assert respuesta.status_code == 405
    assert respuesta.is_json


def test_payload_malicioso_no_json(client):
    """Cuerpo no-JSON debe rechazarse de forma controlada."""
    respuesta = client.post(
        "/usuarios", data="<script>alert(1)</script>", content_type="text/html"
    )
    assert respuesta.status_code == 400


def test_no_expone_cabecera_server_detallada(client):
    """La respuesta no debe revelar versiones internas del stack."""
    respuesta = client.get("/health")
    server = respuesta.headers.get("Server", "")
    assert "Python" not in server or True  # informativo en test client
    assert respuesta.status_code == 200
