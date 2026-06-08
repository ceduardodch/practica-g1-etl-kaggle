# Practica G1 - ETL con Kaggle, Docker, PostgreSQL y Python

Proyecto para el componente practico de Semana 1. Usa datos publicos de Kaggle del dominio ecommerce/ventas:

- Dataset: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- Fuente de busqueda: [Kaggle Search](https://www.kaggle.com/search)
- Repositorio: publico para revision academica

## Entregables

- `docker-compose.yml`
- `.env` con credenciales locales de practica
- `desarrolloG1.ipynb`
- `scripts/` para descarga, carga ETL y generacion de reporte
- `evidencias/` con capturas de ejecucion
- `output/pdf/informe_practica_g1.pdf`

## Como ejecutar

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/download_data.py
docker compose up -d
.venv/bin/python scripts/load_postgres.py
.venv/bin/python scripts/create_notebook.py
.venv/bin/python scripts/generate_report.py
```

## Fuentes principales usadas en el notebook

1. PostgreSQL: tabla `order_items`, cargada desde `olist_order_items_dataset.csv`.
2. CSV: archivo `data/raw/olist_orders_dataset.csv`.
3. JSON: archivo `data/raw/product_categories.json`, generado desde datos Kaggle de categorias.

## Nota de seguridad

El archivo `.env` contiene credenciales locales no sensibles para una base de datos de practica dentro de Docker. No deben reutilizarse en produccion.

