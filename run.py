"""Punto de entrada de la aplicacion.

Local:   python run.py
Render:  gunicorn run:app
"""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # DEBUG controlado por variable de entorno (NUNCA hardcodeado - requisito Bandit)
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=debug_mode)
