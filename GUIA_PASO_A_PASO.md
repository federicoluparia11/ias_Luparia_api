# Guía paso a paso — TP Implementación y Actualización de Software (CI/CD)

Esta guía cubre todo el proceso de punta a punta: configuración local, GitHub, Render, el flujo de ramas "IAS" y la demo del día de la entrega.

> **Importante:** en todos lados donde diga `apellido`, reemplazalo por tu apellido real (ej: `ias_gomez_api`, `gomez_api-dev`).

---

## FASE 1 — Entorno local

1. Verificá los requisitos: Python 3.x (`python --version`), Git (`git --version`) y Visual Studio Code instalados.
2. Descomprimí el proyecto en una carpeta de trabajo y renombrá la carpeta a `ias_apellido_api`.
3. Abrí la carpeta en VS Code y desde la terminal integrada creá el entorno virtual:

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements-dev.txt
```

4. Probá la API localmente:

```bash
python run.py
```

Abrí en el navegador `http://127.0.0.1:5000/health` — deberías ver `{"status": "ok", ...}`.

5. Corré los tests y Bandit para verificar que todo pasa antes de subir nada:

```bash
pytest tests/unit -v
pytest tests/integration -v
pytest tests/security -v
bandit -r app run.py -ll
```

Los 33 tests deben pasar y Bandit debe terminar con 0 issues Medium/High.

---

## FASE 2 — Repositorio en GitHub

### 2.1 Crear el repositorio

1. En GitHub → **New repository** → nombre: `ias_apellido_api` (público o privado, da igual mientras el docente pueda verlo).
2. NO inicialices con README (ya lo tenés en el proyecto).

### 2.2 Subir el código y crear las ramas

Desde la carpeta del proyecto:

```bash
git init
git add .
git commit -m "Estructura inicial de la API y pipelines CI/CD"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/ias_apellido_api.git
git push -u origin main

# Crear la rama develop a partir de main
git checkout -b develop
git push -u origin develop
```

Con esto quedan las dos ramas base del flujo IAS: `main` (QA/PRD) y `develop` (DEV).

### 2.3 Configurar los Secrets

En el repo: **Settings → Secrets and variables → Actions → New repository secret**. Creá estos tres (los valores los obtenés en la Fase 3, paso 3.3 — podés volver acá después):

| Secret | Valor |
|--------|-------|
| `RENDER_DEPLOY_HOOK_DEV` | Deploy hook del servicio DEV de Render |
| `RENDER_DEPLOY_HOOK_QA` | Deploy hook del servicio QA de Render |
| `RENDER_DEPLOY_HOOK_PRD` | Deploy hook del servicio PRD de Render |

### 2.4 Configurar el environment `production` (aprobación manual)

1. **Settings → Environments → New environment** → nombre exacto: `production`.
2. Tildá **Required reviewers** y agregate a vos mismo como reviewer.
3. Guardá con **Save protection rules**.

Esto es lo que hace que el job `deploy-prd` del workflow `cd-qa-prd.yml` quede **en espera** hasta que el Release Manager (vos) apruebe manualmente.

### 2.5 (Recomendado) Proteger las ramas

**Settings → Branches → Add branch protection rule** para `main` y `develop`:
- Tildá *Require a pull request before merging*.
- Tildá *Require status checks to pass before merging* y seleccioná los jobs del CI.

Esto fuerza el "uso correcto de PR" que pesa 30% en la evaluación.

---

## FASE 3 — Render (DEV, QA y PRD)

### 3.1 Crear la base de datos Postgres

1. En el dashboard de Render → **New → PostgreSQL**.
2. Nombre: `apellido_db`. Plan: **Free**.
3. Una vez creada, copiá la **Internal Database URL** (la vas a usar en los 3 servicios).

> Recordá lo que dice el TP: la base expira al mes y solo podés tener una en el plan gratuito, así que los 3 entornos apuntan a la misma base. Anotá los pasos de recreación como plan de contingencia: crear DB nueva → copiar la nueva URL → actualizar `DATABASE_URL` en los 3 servicios → redeploy.

### 3.2 Crear los 3 Web Services

Repetí esto 3 veces (DEV, QA, PRD). **New → Web Service** → conectá tu cuenta de GitHub y elegí el repo `ias_apellido_api`.

| Setting | DEV | QA | PRD |
|---------|-----|-----|-----|
| Name | `apellido_api-dev` | `apellido_api-qa` | `apellido_api-prd` |
| Branch | `develop` | `main` | `main` |
| Build Command | `pip install -r requirements-dev.txt` | `pip install -r requirements-dev.txt` | `pip install -r requirements.txt` |
| Start Command | `gunicorn run:app` | `gunicorn run:app` | `gunicorn run:app` |
| **Auto-Deploy** | **OFF** | **OFF** | **OFF** |
| Plan | Free | Free | Free |

En **Environment Variables** de cada servicio agregá:

| Variable | Valor |
|----------|-------|
| `DATABASE_URL` | la Internal Database URL de tu Postgres |
| `ENV_NAME` | `dev` / `qa` / `prd` según el servicio |

> Auto-Deploy en OFF es clave: los deploys los dispara **únicamente** GitHub Actions vía deploy hooks, que es justamente lo que evalúa el TP.

### 3.3 Obtener los Deploy Hooks

En cada servicio: **Settings → Deploy Hook** → copiá la URL. Cargá cada una como secret en GitHub (paso 2.3):
- Hook de `apellido_api-dev` → `RENDER_DEPLOY_HOOK_DEV`
- Hook de `apellido_api-qa` → `RENDER_DEPLOY_HOOK_QA`
- Hook de `apellido_api-prd` → `RENDER_DEPLOY_HOOK_PRD`

---

## FASE 4 — Flujo de trabajo IAS (el corazón del TP)

### 4.1 Desarrollar en una feature branch

```bash
git checkout develop
git pull
git checkout -b feature/endpoint-usuarios
# ... hacés cambios (ej: agregar un campo, mejorar una validación) ...
git add .
git commit -m "feat: agrega validacion de email en alta de usuario"
git push -u origin feature/endpoint-usuarios
```

### 4.2 PR de feature → develop (camino a DEV)

1. En GitHub → **Pull requests → New pull request** → base: `develop`, compare: `feature/endpoint-usuarios`.
2. Al crearlo se dispara el **CI**: tests unitarios, tests de integración y Bandit (los de seguridad NO, porque el destino no es main).
3. Hacé el **code review** (revisá el diff, dejá un comentario como evidencia) y aprobá.
4. **Merge pull request** → automáticamente corre `cd-dev.yml` → **deploy a DEV**.
5. Verificá en el navegador: `https://apellido_api-dev.onrender.com/health` (la primera vez puede tardar varios minutos en levantar — plan gratuito, lo dice el propio TP).

### 4.3 PR de develop → main (camino a QA)

1. **New pull request** → base: `main`, compare: `develop`.
2. Se dispara el CI completo: unitarios + integración + Bandit + **tests de seguridad** (ahora sí, porque `github.base_ref == 'main'`).
3. Review → approve → **Merge**.
4. Automáticamente corre `cd-qa-prd.yml`: el job `deploy-qa` despliega a QA.
5. Verificá `https://apellido_api-qa.onrender.com/health`.

### 4.4 Aprobación manual y deploy a PRD (rol Release Manager)

1. En el mismo run del workflow, el job **deploy-prd** queda en estado *Waiting* (amarillo) porque el environment `production` exige reviewers.
2. Como Release Manager, **antes de aprobar verificá**: que QA responde correctamente, que no hay errores críticos y que el sistema está estable (probá `/health` y un alta/listado en QA).
3. En la pestaña **Actions** → entrá al run → botón **Review deployments** → tildá `production` → **Approve and deploy**.
4. El job dispara el hook de PRD. Verificá `https://apellido_api-prd.onrender.com/health`.

---

## FASE 5 — Día de la entrega (evidencias en vivo)

Checklist de la demo, en este orden:

1. ☐ Mostrar el repositorio: estructura (`app/`, `tests/unit|integration|security`, `requirements*.txt`, `.github/workflows/`).
2. ☐ Crear una feature branch con un cambio chico (ej: agregar un campo al `/health`).
3. ☐ Crear el **PR feature → develop** y mostrar el CI ejecutándose (Actions).
4. ☐ Aprobar, mergear y mostrar el **deploy a DEV** + la URL de DEV respondiendo JSON.
5. ☐ Crear el **PR develop → main**, mostrar que ahora también corren los **tests de seguridad**.
6. ☐ Mergear y mostrar el **deploy a QA** + la URL de QA.
7. ☐ Mostrar el job de PRD en *Waiting*, verificar QA, y hacer la **aprobación manual**.
8. ☐ Mostrar el **deploy a PRD** + la URL de PRD respondiendo.

> Tip por el plan gratuito de Render: **30-40 minutos antes de la demo**, abrí las 3 URLs `/health` para "despertar" los servicios y que no tarden minutos en levantar frente al docente. Tenelas en pestañas abiertas.

---

## Cómo cumple el proyecto cada requisito del TP

| Requisito del TP | Dónde está resuelto |
|------------------|---------------------|
| Flask + respuesta JSON | `app/` — todos los endpoints devuelven JSON |
| Al menos 3 endpoints + healthcheck | 6 endpoints: `/health` + ABM completo de usuarios |
| Pytest | `tests/unit`, `tests/integration`, `tests/security` (33 tests) |
| Bandit sin errores críticos | Verificado: 0 issues. Job `analisis-bandit` con `-ll` falla el CI ante Medium/High |
| Variables de entorno, sin `debug=True` hardcodeado | `run.py` usa `FLASK_DEBUG`; config vía `DATABASE_URL`/`ENV_NAME` |
| CI en PRs | `.github/workflows/ci.yml` (`on: pull_request` hacia develop y main) |
| Tests de seguridad solo en PR develop→main | Condición `if: github.base_ref == 'main'` en `ci.yml` |
| Deploy automático a DEV tras merge a develop | `cd-dev.yml` (`on: push: develop`) |
| Deploy automático a QA tras merge a main | `cd-qa-prd.yml`, job `deploy-qa` |
| Deploy a PRD con aprobación manual | Job `deploy-prd` con `environment: production` (required reviewers) |
| Estructura sugerida del repo | Respetada: `app/`, `tests/{unit,integration,security}`, requirements, workflows |
