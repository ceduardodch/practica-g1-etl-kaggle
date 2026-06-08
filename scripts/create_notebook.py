from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient


NOTEBOOK_PATH = Path("desarrolloG1.ipynb")


def md(text: str):
    return nbf.v4.new_markdown_cell(text)


def code(text: str):
    return nbf.v4.new_code_cell(text)


def build_notebook():
    nb = nbf.v4.new_notebook()
    nb["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nb["metadata"]["language_info"] = {"name": "python", "pygments_lexer": "ipython3"}

    cells = [
        md(
            "# Desarrollo G1 - Practica ETL Semana 1\n"
            "\n"
            "Dominio de negocio: ecommerce/ventas.\n"
            "\n"
            "Fuente de datos: Kaggle, dataset `olistbr/brazilian-ecommerce`.\n"
            "\n"
            "Objetivo: preparar un entorno ETL con Docker, PostgreSQL y Python, generar tres DataFrames principales y analizar valores nulos, estadisticos y agrupaciones."
        ),
        md(
            "## 1. Configuracion inicial\n"
            "\n"
            "Se cargan librerias, variables de entorno y rutas de trabajo. La base PostgreSQL se levanta con `docker-compose.yml` y sus credenciales se leen desde `.env`."
        ),
        code(
            "from pathlib import Path\n"
            "import json\n"
            "import os\n"
            "\n"
            "import pandas as pd\n"
            "from dotenv import load_dotenv\n"
            "from sqlalchemy import create_engine\n"
            "\n"
            "load_dotenv()\n"
            "RAW_DIR = Path('data/raw')\n"
            "postgres_url = (\n"
            "    f\"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}\"\n"
            "    f\"@{os.environ.get('POSTGRES_HOST', 'localhost')}:{os.environ.get('POSTGRES_PORT', '5432')}/{os.environ['POSTGRES_DB']}\"\n"
            ")\n"
            "engine = create_engine(postgres_url)\n"
            "RAW_DIR.exists(), sorted(p.name for p in RAW_DIR.iterdir())"
        ),
        md(
            "## 2. DataFrame 1 - PostgreSQL: order_items\n"
            "\n"
            "Este DataFrame se consulta desde la tabla `order_items` cargada en PostgreSQL. La fuente original es el archivo CSV de Kaggle `olist_order_items_dataset.csv`, convertido previamente a tabla de base de datos."
        ),
        code(
            "df_order_items_pg = pd.read_sql('SELECT * FROM order_items', engine)\n"
            "df_order_items_pg.head()"
        ),
        code(
            "pd.DataFrame({\n"
            "    'columna': df_order_items_pg.columns,\n"
            "    'tiene_nulos': df_order_items_pg.isna().any().values,\n"
            "    'valores_faltantes': df_order_items_pg.isna().sum().values,\n"
            "})"
        ),
        code(
            "df_order_items_pg[['price', 'freight_value']].agg(['mean', 'max', 'min']).round(2)"
        ),
        code(
            "df_order_items_pg.groupby('seller_id')[['price', 'freight_value']].agg(['max', 'min']).head(10).round(2)"
        ),
        md(
            "## 3. DataFrame 2 - CSV: orders\n"
            "\n"
            "Este DataFrame se lee directamente desde el archivo CSV `olist_orders_dataset.csv`. Se parsean fechas para calcular dias de procesamiento entre compra y entrega al transportista."
        ),
        code(
            "date_cols = ['order_purchase_timestamp', 'order_delivered_carrier_date']\n"
            "df_orders_csv = pd.read_csv(RAW_DIR / 'olist_orders_dataset.csv', parse_dates=date_cols)\n"
            "df_orders_csv['processing_days'] = (\n"
            "    df_orders_csv['order_delivered_carrier_date'] - df_orders_csv['order_purchase_timestamp']\n"
            ").dt.total_seconds() / 86400\n"
            "df_orders_csv.head()"
        ),
        code(
            "pd.DataFrame({\n"
            "    'columna': df_orders_csv.columns,\n"
            "    'tiene_nulos': df_orders_csv.isna().any().values,\n"
            "    'valores_faltantes': df_orders_csv.isna().sum().values,\n"
            "})"
        ),
        code(
            "df_orders_csv[['processing_days']].agg(['mean', 'max', 'min']).round(2)"
        ),
        code(
            "df_orders_csv.groupby('order_status')[['processing_days']].agg(['max', 'min']).round(2)"
        ),
        md(
            "## 4. DataFrame 3 - JSON: product_categories\n"
            "\n"
            "Este DataFrame se genera desde `product_categories.json`, archivo JSON creado a partir de la tabla de traduccion de categorias del dataset Kaggle. Se agregaron campos numericos de longitud de texto para poder analizar metricas."
        ),
        code(
            "df_categories_json = pd.read_json(RAW_DIR / 'product_categories.json')\n"
            "df_categories_json.head()"
        ),
        code(
            "pd.DataFrame({\n"
            "    'columna': df_categories_json.columns,\n"
            "    'tiene_nulos': df_categories_json.isna().any().values,\n"
            "    'valores_faltantes': df_categories_json.isna().sum().values,\n"
            "})"
        ),
        code(
            "df_categories_json[['category_name_length', 'english_name_length']].agg(['mean', 'max', 'min']).round(2)"
        ),
        code(
            "df_categories_json.groupby('first_letter')[['category_name_length', 'english_name_length']].agg(['max', 'min']).head(10).round(2)"
        ),
        md(
            "## 5. Observaciones generales\n"
            "\n"
            "- El flujo integra fuentes heterogeneas: PostgreSQL, CSV y JSON.\n"
            "- Los datos de ventas permiten medir precios, fletes, estados de orden y categorias de producto.\n"
            "- La separacion entre descarga, carga y analisis facilita repetir el ETL sin rehacer el proyecto manualmente."
        ),
        md(
            "# Aplicacion Profesional de la Practica\n"
            "\n"
            "## Carlos Diaz\n"
            "\n"
            "En mi contexto profesional me interesa aplicar estos conocimientos en areas de ecommerce, operaciones digitales y automatizacion comercial. En estos entornos se generan datos de ventas, productos, clientes, pagos, conversaciones de WhatsApp, campanas publicitarias, costos de envio, estados de entrega y eventos de seguimiento. Estos datos normalmente viven en sistemas separados, por ejemplo plataformas de tienda, hojas de calculo, bases transaccionales, CRMs, APIs de publicidad y archivos descargados manualmente.\n"
            "\n"
            "PostgreSQL, Docker y Python pueden organizar ese flujo de una manera mas profesional. Docker permite levantar una base de datos aislada y repetible, sin depender de configuraciones manuales de una computadora especifica. PostgreSQL sirve como repositorio estructurado para almacenar tablas limpias de pedidos, productos, clientes o pagos. Python permite automatizar la lectura de archivos CSV y JSON, transformar columnas, validar valores faltantes, calcular indicadores y cargar resultados hacia la base de datos.\n"
            "\n"
            "Implementar un proceso ETL aportaria orden, trazabilidad y velocidad. En lugar de revisar reportes desconectados, la organizacion podria tener un flujo donde los datos se extraen desde sus fuentes, se transforman con reglas claras y se cargan en una base lista para analisis. Esto reduce errores humanos, mejora la consistencia de los reportes y permite repetir el proceso cada semana o cada dia.\n"
            "\n"
            "Con la informacion integrada se podrian resolver decisiones concretas: identificar productos con mejor margen, detectar demoras logisticas, comparar desempeno por canal de venta, medir conversion real de campanas, encontrar pedidos con problemas y priorizar acciones comerciales. Tambien se podrian crear tableros de seguimiento para que gerencia vea ventas, costos y cumplimiento operativo con datos actualizados. En resumen, la practica conecta herramientas tecnicas con una necesidad real: convertir datos dispersos en informacion confiable para decidir mejor."
        ),
    ]
    nb["cells"] = cells
    return nb


def main() -> None:
    nb = build_notebook()
    client = NotebookClient(nb, timeout=600, kernel_name="python3")
    executed = client.execute()
    nbf.write(executed, NOTEBOOK_PATH)
    print(f"created and executed {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()

