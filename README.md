# ias_apellido_api

API REST de gestion de usuarios (ABM) desarrollada para el cliente ficticio de la empresa **IAS**, con pipeline completo de CI/CD.

> Reemplazar `apellido` por tu apellido real en el nombre del repositorio.

## Stack

- Python 3.x + Flask
- SQLAlchemy (PostgreSQL en Render / SQLite local)
- Pytest (tests unitarios, de integracion y de seguridad)
- Bandit (analisis estatico de seguridad)
- GitHub Actions (CI/CD)
- Render (DEV / QA / PRD)

## Endpoints

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/health` | Healthcheck del servicio |
| GET | `/usuarios` | Lista todos los usuarios |
| GET | `/usuarios/<id>` | Obtiene un usuario |
| POST | `/usuarios` | Crea un usuario (`{"nombre": "...", "email": "..."}`) |
| PUT | `/usuarios/<id>` | Actualiza un usuario |
| DELETE | `/usuarios/<id>` | Elimina un usuario |

Todas las respuestas son JSON.

## Ejecucion local

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
python run.py                   # http://127.0.0.1:5000/health
```

## Tests

```bash
pytest tests/unit -v          # unitarios
pytest tests/integration -v   # integracion
pytest tests/security -v      # seguridad
bandit -r app run.py -ll      # analisis estatico
```

## Flujo CI/CD (estandar IAS)

1. `feature/*` -> PR a `develop` -> CI (unit + integracion + Bandit) -> review -> merge -> **deploy automatico a DEV**
2. `develop` -> PR a `main` -> CI (+ tests de seguridad) -> review -> merge -> **deploy automatico a QA**
3. Aprobacion manual del Release Manager (environment `production`) -> **deploy a PRD**

## Variables de entorno

| Variable | Descripcion |
|----------|-------------|
| `DATABASE_URL` | URL de PostgreSQL (Render) - local usa SQLite |
| `ENV_NAME` | `dev`, `qa` o `prd` (se muestra en `/health`) |
| `FLASK_DEBUG` | `1` solo en local; nunca en remoto |
| `PORT` | Puerto (lo define Render) |
