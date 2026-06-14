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

    nb["cells"] = [
        md(
            "# Desarrollo G1 - Practica ETL Semana 1\n\n"
            "Dominio de negocio: ciberseguridad y monitoreo de incidentes de red.\n\n"
            "Fuente de datos: Kaggle, dataset `teamincribo/cyber-security-attacks`.\n\n"
            "Objetivo: configurar PostgreSQL en Docker, cargar una tabla de hechos de alertas de red y analizar tres fuentes relacionadas: PostgreSQL, CSV y JSON."
        ),
        md(
            "## 1. Configuracion inicial\n\n"
            "Las credenciales de PostgreSQL se leen desde `.env`. Esto evita escribir usuarios, claves o puertos directamente en las celdas del notebook."
        ),
        code(
            "from pathlib import Path\n"
            "import os\n\n"
            "import pandas as pd\n"
            "from dotenv import load_dotenv\n"
            "from sqlalchemy import create_engine\n\n"
            "load_dotenv()\n"
            "RAW_DIR = Path('data/raw')\n"
            "postgres_url = (\n"
            "    f\"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}\"\n"
            "    f\"@{os.environ.get('POSTGRES_HOST', 'localhost')}:{os.environ.get('POSTGRES_PORT', '5432')}/{os.environ['POSTGRES_DB']}\"\n"
            ")\n"
            "engine = create_engine(postgres_url)\n"
            "sorted(p.name for p in RAW_DIR.iterdir())"
        ),
        md(
            "## 2. DataFrame 1 - PostgreSQL: network_alerts\n\n"
            "Este DataFrame proviene de la base PostgreSQL levantada con Docker. La tabla `network_alerts` funciona como tabla de hechos del proyecto SOC, con eventos, protocolos, severidad, tamano de paquete y puntajes de anomalia."
        ),
        code("df_alerts_pg = pd.read_sql('SELECT * FROM network_alerts', engine)\ndf_alerts_pg.head(5)"),
        code(
            "pd.DataFrame({\n"
            "    'columna': df_alerts_pg.columns,\n"
            "    'tiene_nulos': df_alerts_pg.isna().any().values,\n"
            "    'valores_faltantes': df_alerts_pg.isna().sum().values,\n"
            "})"
        ),
        code("df_alerts_pg[['packet_length', 'anomaly_scores']].agg(['mean', 'max', 'min']).round(2)"),
        code(
            "(\n"
            "    df_alerts_pg.groupby(['protocol', 'severity_level'])[['packet_length', 'anomaly_scores']]\n"
            "    .agg(['max', 'min']).head(12).round(2)\n"
            ")"
        ),
        md(
            "## 3. DataFrame 2 - CSV: asset_inventory\n\n"
            "Este DataFrame representa el inventario de activos de infraestructura. Se relaciona con `network_alerts` mediante `machine_id`, creado a partir de la IP destino de las alertas."
        ),
        code("df_assets_csv = pd.read_csv(RAW_DIR / 'asset_inventory.csv')\ndf_assets_csv.head(5)"),
        code(
            "pd.DataFrame({\n"
            "    'columna': df_assets_csv.columns,\n"
            "    'tiene_nulos': df_assets_csv.isna().any().values,\n"
            "    'valores_faltantes': df_assets_csv.isna().sum().values,\n"
            "})"
        ),
        code(
            "df_assets_csv['criticality_score'] = df_assets_csv['criticality'].map({'Low': 1, 'Medium': 2, 'High': 3}).fillna(0)\n"
            "df_assets_csv[['criticality_score']].agg(['mean', 'max', 'min']).round(2)"
        ),
        code(
            "(\n"
            "    df_assets_csv.groupby(['department', 'operating_system'])[['criticality_score']]\n"
            "    .agg(['max', 'min']).head(12).round(2)\n"
            ")"
        ),
        md(
            "## 4. DataFrame 3 - JSON: vulnerability_catalog\n\n"
            "Este DataFrame se lee desde `vulnerability_catalog.json`. El catalogo mapea tipos de ataque y protocolos con CVE simulados, puntaje CVSS y accion de remediacion. Se relaciona con las alertas mediante `attack_type`, `protocol` y `severity_level`."
        ),
        code("df_vulns_json = pd.read_json(RAW_DIR / 'vulnerability_catalog.json')\ndf_vulns_json.head(5)"),
        code(
            "pd.DataFrame({\n"
            "    'columna': df_vulns_json.columns,\n"
            "    'tiene_nulos': df_vulns_json.isna().any().values,\n"
            "    'valores_faltantes': df_vulns_json.isna().sum().values,\n"
            "})"
        ),
        code("df_vulns_json[['cvss_score']].agg(['mean', 'max', 'min']).round(2)"),
        code(
            "(\n"
            "    df_vulns_json.groupby(['protocol', 'severity_level'])[['cvss_score']]\n"
            "    .agg(['max', 'min']).head(12).round(2)\n"
            ")"
        ),
        md(
            "## 5. Relacion entre fuentes\n\n"
            "Se integran las tres fuentes para responder preguntas de inteligencia de negocio en un contexto SOC: que departamentos concentran mas alertas, que protocolos tienen mayor riesgo y que activos requieren priorizacion."
        ),
        code(
            "df_integrated = (\n"
            "    df_alerts_pg.merge(df_assets_csv, on='machine_id', how='left')\n"
            "    .merge(df_vulns_json, on=['attack_type', 'protocol', 'severity_level'], how='left')\n"
            ")\n"
            "(\n"
            "    df_integrated.groupby(['department', 'severity_level'])[['anomaly_scores', 'cvss_score']]\n"
            "    .agg(['mean', 'max', 'min', 'count']).round(2).head(12)\n"
            ")"
        ),
        md(
            "# Aplicacion Profesional de la Practica\n\n"
            "## Carlos Diaz\n\n"
            "En mi contexto profesional, esta practica puede aplicarse directamente al area de infraestructura tecnologica, operaciones cloud y ciberseguridad. En este tipo de entorno se generan datos de logs de red, eventos de firewall, alertas IDS/IPS, inventario de servidores, sistemas operativos, direcciones IP, severidad de incidentes, acciones tomadas y vulnerabilidades asociadas. Normalmente estos datos se encuentran dispersos entre consolas, archivos CSV, servicios cloud, herramientas de monitoreo y reportes manuales.\n\n"
            "PostgreSQL, Docker y Python permiten ordenar ese ecosistema. Docker facilita levantar una base de datos reproducible para pruebas o analisis sin depender de configuraciones manuales de una sola computadora. PostgreSQL permite almacenar de forma estructurada las alertas y consultarlas con criterios consistentes. Python ayuda a extraer archivos de Kaggle u otras fuentes, transformar columnas, detectar nulos, crear claves de relacion y generar indicadores de riesgo.\n\n"
            "Un proceso ETL aportaria trazabilidad, repetibilidad y mejor toma de decisiones. En vez de revisar logs aislados, la organizacion podria integrar alertas, activos y vulnerabilidades en un modelo comun. Esto ayudaria a identificar departamentos con mayor exposicion, protocolos mas atacados, servidores criticos con alertas recurrentes y vulnerabilidades que requieren remediacion prioritaria.\n\n"
            "Con esta informacion se podrian resolver problemas concretos: priorizar parches, reducir falsos positivos, justificar inversiones de seguridad, definir reglas de firewall, medir el comportamiento de incidentes por segmento de red y entregar reportes ejecutivos basados en evidencia. La practica demuestra como pasar de archivos sueltos a informacion confiable para operar mejor un entorno tecnologico."
        ),
    ]
    return nb


def main() -> None:
    nb = build_notebook()
    client = NotebookClient(nb, timeout=600, kernel_name="python3")
    executed = client.execute()
    nbf.write(executed, NOTEBOOK_PATH)
    print(f"created and executed {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
