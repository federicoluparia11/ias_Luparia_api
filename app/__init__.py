"""Fabrica de la aplicacion Flask - API de usuarios (empresa IAS)."""
import os

from flask import Flask, jsonify

from .extensions import db


def create_app(config_override=None):
    """Crea y configura la aplicacion Flask (patron application factory)."""
    app = Flask(__name__)

    # Configuracion via variables de entorno (requisito Bandit / IAS)
    database_url = os.environ.get("DATABASE_URL", "sqlite:///local.db")
    # Render entrega URLs con esquema postgres:// (SQLAlchemy requiere postgresql://)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["ENV_NAME"] = os.environ.get("ENV_NAME", "local")

    if config_override:
        app.config.update(config_override)

    db.init_app(app)

    from .routes import api
    app.register_blueprint(api)

    # Manejo de errores con respuesta JSON
    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(400)
    def bad_request(error):
        descripcion = getattr(error, "description", "Solicitud invalida")
        return jsonify({"error": descripcion}), 400

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"error": "Metodo no permitido"}), 405

    with app.app_context():
        db.create_all()

    return app
