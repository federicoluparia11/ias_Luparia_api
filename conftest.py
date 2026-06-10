"""Fixtures compartidas para todos los tests."""
import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app():
    """Instancia de la app con base de datos SQLite en memoria."""
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "ENV_NAME": "test",
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """Cliente HTTP de prueba de Flask."""
    return app.test_client()
