"""Tests de integracion: endpoints completos contra DB en memoria."""


def test_healthcheck(client):
    respuesta = client.get("/health")
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    assert datos["status"] == "ok"
    assert datos["version"] == "1.1.0"
    assert "environment" in datos


def test_listar_usuarios_vacio(client):
    respuesta = client.get("/usuarios")
    assert respuesta.status_code == 200
    assert respuesta.get_json() == []


def test_crear_usuario(client):
    respuesta = client.post(
        "/usuarios", json={"nombre": "Ana Garcia", "email": "ana@mail.com"}
    )
    assert respuesta.status_code == 201
    datos = respuesta.get_json()
    assert datos["nombre"] == "Ana Garcia"
    assert datos["email"] == "ana@mail.com"
    assert "id" in datos


def test_crear_usuario_email_duplicado(client):
    client.post("/usuarios", json={"nombre": "Ana", "email": "ana@mail.com"})
    respuesta = client.post("/usuarios", json={"nombre": "Otra", "email": "ana@mail.com"})
    assert respuesta.status_code == 409


def test_crear_usuario_payload_invalido(client):
    respuesta = client.post("/usuarios", json={"nombre": "", "email": "no-es-email"})
    assert respuesta.status_code == 400
    assert "error" in respuesta.get_json()


def test_obtener_usuario(client):
    creado = client.post(
        "/usuarios", json={"nombre": "Ana", "email": "ana@mail.com"}
    ).get_json()
    respuesta = client.get(f"/usuarios/{creado['id']}")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["email"] == "ana@mail.com"


def test_obtener_usuario_inexistente(client):
    respuesta = client.get("/usuarios/9999")
    assert respuesta.status_code == 404


def test_actualizar_usuario(client):
    creado = client.post(
        "/usuarios", json={"nombre": "Ana", "email": "ana@mail.com"}
    ).get_json()
    respuesta = client.put(
        f"/usuarios/{creado['id']}",
        json={"nombre": "Ana Maria", "email": "ana.maria@mail.com"},
    )
    assert respuesta.status_code == 200
    assert respuesta.get_json()["nombre"] == "Ana Maria"


def test_eliminar_usuario(client):
    creado = client.post(
        "/usuarios", json={"nombre": "Ana", "email": "ana@mail.com"}
    ).get_json()
    respuesta = client.delete(f"/usuarios/{creado['id']}")
    assert respuesta.status_code == 200
    assert client.get(f"/usuarios/{creado['id']}").status_code == 404


def test_flujo_abm_completo(client):
    """Alta -> consulta -> modificacion -> baja (ABM completo)."""
    alta = client.post("/usuarios", json={"nombre": "Caro", "email": "caro@mail.com"})
    assert alta.status_code == 201
    uid = alta.get_json()["id"]

    assert len(client.get("/usuarios").get_json()) == 1

    mod = client.put(f"/usuarios/{uid}", json={"nombre": "Carolina", "email": "caro@mail.com"})
    assert mod.status_code == 200

    baja = client.delete(f"/usuarios/{uid}")
    assert baja.status_code == 200
    assert client.get("/usuarios").get_json() == []
