# Practica G1 - ETL de Ciberseguridad con Kaggle, Docker, PostgreSQL y Python

Proyecto academico para los componentes practicos de Semana 1 y Semana 2. El dominio seleccionado es ciberseguridad y monitoreo de incidentes de red.

- Dataset base: [Cyber Security Attacks](https://www.kaggle.com/datasets/teamincribo/cyber-security-attacks)
- Fuente de busqueda: [Kaggle Search](https://www.kaggle.com/search)
- Tabla PostgreSQL: `network_alerts`
- CSV obligatorio: `data/raw/asset_inventory.csv`
- JSON: `data/raw/vulnerability_catalog.json`

## Entregables

- `docker-compose.yml`
- `.env` con credenciales locales de practica
- `desarrolloG1.ipynb` para Semana 1
- `TransformG1.ipynb` para Semana 2
- `scripts/` para descarga, carga ETL y generacion de notebooks/informe
- `evidencias/` con capturas de ejecucion
- `output/pdf/informe_practica_g1.pdf`

## Ejecucion rapida

Requisitos: Git, Docker Desktop o Docker Engine, Docker Compose y Python 3.

```bash
git clone https://github.com/ceduardodch/practica-g1-etl-kaggle.git
cd practica-g1-etl-kaggle
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/download_data.py
docker compose up -d
.venv/bin/python scripts/load_postgres.py
.venv/bin/python scripts/create_notebook.py
.venv/bin/python scripts/create_transform_notebook.py
.venv/bin/python scripts/generate_report.py
```

## Fuentes de datos

1. PostgreSQL: `network_alerts`, tabla de hechos de alertas de red cargada desde Kaggle.
2. CSV: `asset_inventory.csv`, inventario de activos relacionado mediante `machine_id`.
3. JSON: `vulnerability_catalog.json`, catalogo de vulnerabilidades relacionado por `attack_type`, `protocol` y `severity_level`.

## Nota sobre el puerto

PostgreSQL corre dentro del contenedor en `5432`, pero se expone localmente en `5433` porque el puerto `5432` puede estar ocupado por instalaciones locales. Si otra computadora ya usa `5433`, cambie `POSTGRES_PORT` en `.env`.

## Nota de seguridad

El archivo `.env` contiene credenciales locales no sensibles para practica academica. En produccion no se subirian credenciales a un repositorio.
