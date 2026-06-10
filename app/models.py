"""Modelos de datos de la API."""
from .extensions import db


class Usuario(db.Model):
    """Modelo de usuario para el ABM."""

    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def to_dict(self):
        """Serializa el usuario a diccionario (respuesta JSON)."""
        return {"id": self.id, "nombre": self.nombre, "email": self.email}
