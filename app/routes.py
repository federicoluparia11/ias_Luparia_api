"""Endpoints de la API (ABM de usuarios + healthcheck)."""
from flask import Blueprint, current_app, jsonify, request

from .extensions import db
from .models import Usuario
from .validators import validar_payload_usuario

api = Blueprint("api", __name__)


@api.get("/health")
def healthcheck():
    """Endpoint de healthcheck requerido por el TP."""
    return jsonify(
        {
            "status": "ok",
            "service": "ias-api-usuarios",
            "version": "1.1.0"
            "environment": current_app.config.get("ENV_NAME", "local"),
        }
    ), 200
        


        
@api.get("/usuarios")
def listar_usuarios():
    """Lista todos los usuarios."""
    usuarios = Usuario.query.order_by(Usuario.id).all()
    return jsonify([u.to_dict() for u in usuarios]), 200


@api.get("/usuarios/<int:usuario_id>")
def obtener_usuario(usuario_id):
    """Obtiene un usuario por su id."""
    usuario = db.session.get(Usuario, usuario_id)
    if usuario is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(usuario.to_dict()), 200


@api.post("/usuarios")
def crear_usuario():
    """Crea un nuevo usuario (Alta del ABM)."""
    payload = request.get_json(silent=True)
    es_valido, error = validar_payload_usuario(payload)
    if not es_valido:
        return jsonify({"error": error}), 400

    email = payload["email"].strip().lower()
    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "Ya existe un usuario con ese email"}), 409

    usuario = Usuario(nombre=payload["nombre"].strip(), email=email)
    db.session.add(usuario)
    db.session.commit()
    return jsonify(usuario.to_dict()), 201


@api.put("/usuarios/<int:usuario_id>")
def actualizar_usuario(usuario_id):
    """Actualiza un usuario existente (Modificacion del ABM)."""
    usuario = db.session.get(Usuario, usuario_id)
    if usuario is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    payload = request.get_json(silent=True)
    es_valido, error = validar_payload_usuario(payload)
    if not es_valido:
        return jsonify({"error": error}), 400

    email = payload["email"].strip().lower()
    existente = Usuario.query.filter_by(email=email).first()
    if existente and existente.id != usuario.id:
        return jsonify({"error": "Ya existe un usuario con ese email"}), 409

    usuario.nombre = payload["nombre"].strip()
    usuario.email = email
    db.session.commit()
    return jsonify(usuario.to_dict()), 200


@api.delete("/usuarios/<int:usuario_id>")
def eliminar_usuario(usuario_id):
    """Elimina un usuario (Baja del ABM)."""
    usuario = db.session.get(Usuario, usuario_id)
    if usuario is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"mensaje": f"Usuario {usuario_id} eliminado"}), 200
