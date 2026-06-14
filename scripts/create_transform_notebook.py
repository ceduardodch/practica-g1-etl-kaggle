from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient


NOTEBOOK_PATH = Path("TransformG1.ipynb")


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
            "# TransformG1 - Practica ETL Semana 2\n\n"
            "Grupo: G1\n\n"
            "Integrante: Carlos Diaz\n\n"
            "Proyecto: ciberseguridad y monitoreo de incidentes de red. Este notebook documenta limpieza, normalizacion, transformacion y validacion de tres fuentes relacionadas: alertas de red, inventario de activos y catalogo de vulnerabilidades."
        ),
        md(
            "## 1. Exploracion inicial de fuentes\n\n"
            "Se revisan estructura, filas, columnas, tipos de datos, nulos, duplicados y posibles llaves de relacion. Las columnas principales de relacion son `machine_id`, `attack_type`, `protocol` y `severity_level`."
        ),
        code(
            "from pathlib import Path\n"
            "import os\n\n"
            "import pandas as pd\n"
            "from dotenv import load_dotenv\n\n"
            "load_dotenv()\n"
            "RAW_DIR = Path('data/raw')\n"
            "alerts_raw = pd.read_csv(RAW_DIR / 'cybersecurity_attacks.csv')\n"
            "assets_raw = pd.read_csv(RAW_DIR / 'asset_inventory.csv')\n"
            "vulns_raw = pd.read_json(RAW_DIR / 'vulnerability_catalog.json')\n"
            "{\n"
            "    'alerts': alerts_raw.shape,\n"
            "    'assets': assets_raw.shape,\n"
            "    'vulnerabilities': vulns_raw.shape,\n"
            "}"
        ),
        code(
            "summary = []\n"
            "for name, frame in {'alerts': alerts_raw, 'assets': assets_raw, 'vulnerabilities': vulns_raw}.items():\n"
            "    summary.append({\n"
            "        'fuente': name,\n"
            "        'filas': frame.shape[0],\n"
            "        'columnas': frame.shape[1],\n"
            "        'duplicados': frame.duplicated().sum(),\n"
            "        'nulos_totales': frame.isna().sum().sum(),\n"
            "    })\n"
            "pd.DataFrame(summary)"
        ),
        code(
            "pd.concat(\n"
            "    [\n"
            "        alerts_raw.dtypes.rename('alerts'),\n"
            "        assets_raw.dtypes.rename('assets'),\n"
            "        vulns_raw.dtypes.rename('vulnerabilities'),\n"
            "    ],\n"
            "    axis=1,\n"
            ")"
        ),
        md(
            "## 2. Configuracion segura del proyecto\n\n"
            "Las variables de entorno utilizadas son `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` y `POSTGRES_PORT`. No se deben escribir credenciales directamente en notebooks porque pueden subirse por error a repositorios o compartirse con terceros."
        ),
        code(
            "env_check = {\n"
            "    'POSTGRES_DB': bool(os.getenv('POSTGRES_DB')),\n"
            "    'POSTGRES_USER': bool(os.getenv('POSTGRES_USER')),\n"
            "    'POSTGRES_PASSWORD': bool(os.getenv('POSTGRES_PASSWORD')),\n"
            "    'POSTGRES_HOST': bool(os.getenv('POSTGRES_HOST')),\n"
            "    'POSTGRES_PORT': bool(os.getenv('POSTGRES_PORT')),\n"
            "}\n"
            "env_check"
        ),
        md(
            "## 3. Funciones de limpieza\n\n"
            "Se definen funciones reutilizables para corregir nombres de columnas, estandarizar texto, convertir fechas, tratar nulos, eliminar duplicados y limpiar llaves de relacion."
        ),
        code(
            "def to_snake_case(column):\n"
            "    return column.strip().lower().replace('/', '_').replace('-', '_').replace(' ', '_')\n\n"
            "def normalize_text(series):\n"
            "    return series.astype(str).str.strip().str.replace(r'\\\\s+', ' ', regex=True)\n\n"
            "def clean_alerts(frame):\n"
            "    df = frame.copy()\n"
            "    df.columns = [to_snake_case(col) for col in df.columns]\n"
            "    df = df.drop_duplicates()\n"
            "    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')\n"
            "    text_cols = ['protocol', 'traffic_type', 'attack_type', 'severity_level', 'action_taken', 'network_segment']\n"
            "    for col in text_cols:\n"
            "        df[col] = normalize_text(df[col])\n"
            "    df['alerts_warnings'] = df['alerts_warnings'].fillna('No alert')\n"
            "    df['ids_ips_alerts'] = df['ids_ips_alerts'].fillna('No IDS alert')\n"
            "    df['proxy_information'] = df['proxy_information'].fillna('No proxy')\n"
            "    df['machine_id'] = 'SRV-UNTRACKED'\n"
            "    df['alert_natural_key'] = df['attack_type'].str.upper() + '-' + df['protocol'].str.upper()\n"
            "    return df\n\n"
            "def clean_assets(frame):\n"
            "    df = frame.copy()\n"
            "    df.columns = [to_snake_case(col) for col in df.columns]\n"
            "    df = df.drop_duplicates(subset=['machine_id'])\n"
            "    for col in ['machine_id', 'server_name', 'operating_system', 'department', 'network_segment', 'criticality']:\n"
            "        df[col] = normalize_text(df[col])\n"
            "    return df\n\n"
            "def clean_vulnerabilities(frame):\n"
            "    df = frame.copy()\n"
            "    df.columns = [to_snake_case(col) for col in df.columns]\n"
            "    df = df.drop_duplicates(subset=['alert_id'])\n"
            "    for col in ['attack_type', 'protocol', 'severity_level', 'vulnerability_name', 'remediation_action']:\n"
            "        df[col] = normalize_text(df[col])\n"
            "    df['cvss_score'] = pd.to_numeric(df['cvss_score'], errors='coerce').fillna(0)\n"
            "    return df"
        ),
        md(
            "## 4. Seleccion de columnas relevantes\n\n"
            "Se conservan columnas utiles para analisis SOC: tiempo, IPs, protocolo, tamano de paquete, tipo de ataque, severidad, activo, departamento, criticidad y CVSS. Se eliminan textos largos de payload cuando no aportan al indicador principal."
        ),
        code(
            "alerts_clean = clean_alerts(alerts_raw)\n"
            "assets_clean = clean_assets(assets_raw)\n"
            "vulns_clean = clean_vulnerabilities(vulns_raw)\n\n"
            "ip_to_machine = dict(zip(assets_clean['ip_address'], assets_clean['machine_id']))\n"
            "alerts_clean['machine_id'] = alerts_clean['destination_ip_address'].map(ip_to_machine).fillna('SRV-UNTRACKED')\n\n"
            "alerts_selected = alerts_clean[[\n"
            "    'timestamp', 'source_ip_address', 'destination_ip_address', 'protocol', 'packet_length',\n"
            "    'traffic_type', 'anomaly_scores', 'attack_type', 'action_taken', 'severity_level',\n"
            "    'network_segment', 'machine_id', 'alert_natural_key'\n"
            "]]\n"
            "assets_selected = assets_clean[[\n"
            "    'machine_id', 'server_name', 'operating_system', 'department', 'ip_address',\n"
            "    'network_segment', 'criticality', 'log_source'\n"
            "]]\n"
            "vulns_selected = vulns_clean[[\n"
            "    'alert_id', 'attack_type', 'protocol', 'severity_level', 'vulnerability_name',\n"
            "    'cve_code', 'cvss_score', 'remediation_action'\n"
            "]]\n"
            "alerts_selected.head(5)"
        ),
        md(
            "## 5. Transformaciones requeridas\n\n"
            "Se crean columnas derivadas para analizar picos de ataque por hora y dia, categorizar riesgo y clasificar paquetes de red."
        ),
        code(
            "alerts_transformed = alerts_selected.copy()\n"
            "alerts_transformed['event_hour'] = alerts_transformed['timestamp'].dt.hour\n"
            "alerts_transformed['event_weekday'] = alerts_transformed['timestamp'].dt.day_name()\n"
            "alerts_transformed['packet_size_category'] = alerts_transformed['packet_length'].apply(\n"
            "    lambda value: 'large' if value >= 1000 else ('medium' if value >= 500 else 'small')\n"
            ")\n"
            "alerts_transformed['risk_band'] = alerts_transformed['anomaly_scores'].apply(\n"
            "    lambda score: 'high' if score >= 70 else ('medium' if score >= 40 else 'low')\n"
            ")\n\n"
            "vulns_transformed = vulns_selected.copy()\n"
            "vulns_transformed['cvss_band'] = vulns_transformed['cvss_score'].apply(\n"
            "    lambda score: 'critical' if score >= 9 else ('high' if score >= 7 else ('medium' if score >= 4 else 'low'))\n"
            ")\n"
            "alerts_transformed.head(5)"
        ),
        md(
            "## 6. Generacion de identificadores\n\n"
            "Se crean identificadores numericos secuenciales para facilitar integracion posterior en modelos dimensionales o cargas a bases de datos."
        ),
        code(
            "alerts_transformed = alerts_transformed.reset_index(drop=True)\n"
            "assets_selected = assets_selected.reset_index(drop=True)\n"
            "vulns_transformed = vulns_transformed.reset_index(drop=True)\n\n"
            "alerts_transformed.insert(0, 'network_alert_id', range(1, len(alerts_transformed) + 1))\n"
            "assets_selected.insert(0, 'asset_id', range(1, len(assets_selected) + 1))\n"
            "vulns_transformed.insert(0, 'vulnerability_id', range(1, len(vulns_transformed) + 1))\n"
            "alerts_transformed[['network_alert_id', 'timestamp', 'machine_id', 'attack_type', 'risk_band']].head(5)"
        ),
        md(
            "## 7. Validacion de resultados\n\n"
            "Se verifica que los DataFrames transformados no tengan duplicados completos, que las claves principales existan y que los tipos de datos sean consistentes."
        ),
        code(
            "validation = []\n"
            "for name, frame, key in [\n"
            "    ('alerts_transformed', alerts_transformed, 'network_alert_id'),\n"
            "    ('assets_selected', assets_selected, 'asset_id'),\n"
            "    ('vulns_transformed', vulns_transformed, 'vulnerability_id'),\n"
            "]:\n"
            "    validation.append({\n"
            "        'dataframe': name,\n"
            "        'filas': len(frame),\n"
            "        'duplicados': frame.duplicated().sum(),\n"
            "        'nulos_clave': frame[key].isna().sum(),\n"
            "        'nulos_totales': frame.isna().sum().sum(),\n"
            "    })\n"
            "pd.DataFrame(validation)"
        ),
        code(
            "integrated = (\n"
            "    alerts_transformed.merge(assets_selected, on='machine_id', how='left')\n"
            "    .merge(vulns_transformed, on=['attack_type', 'protocol', 'severity_level'], how='left')\n"
            ")\n"
            "integrated[['network_alert_id', 'department', 'operating_system', 'attack_type', 'protocol', 'risk_band', 'cvss_score']].head(10)"
        ),
        code(
            "pd.DataFrame({\n"
            "    'columna': integrated.columns,\n"
            "    'tipo_dato': [str(dtype) for dtype in integrated.dtypes],\n"
            "    'nulos': integrated.isna().sum().values,\n"
            "}).head(30)"
        ),
        md(
            "# Reflexion individual final\n\n"
            "Esta semana aprendi que la transformacion de datos es la etapa que convierte fuentes crudas en informacion confiable para analizar. En un contexto de infraestructura y ciberseguridad, los logs pueden venir con fechas mal formateadas, IPs incompletas, textos inconsistentes, duplicados o campos nulos. Si esos problemas no se corrigen, un reporte de incidentes puede mostrar prioridades equivocadas o esconder riesgos reales.\n\n"
            "En mi entorno profesional podria aplicar esta practica para normalizar eventos de red, inventarios de servidores, alertas de firewall y catalogos de vulnerabilidades. Usaria funciones de limpieza para estandarizar nombres de columnas, convertir fechas, eliminar duplicados, categorizar severidades y crear identificadores que permitan relacionar fuentes. Documentar cada paso en un notebook es importante porque deja evidencia del criterio usado y permite que otro integrante revise, repita o mejore el proceso. Esto aporta a la toma de decisiones porque ayuda a priorizar parches, detectar segmentos con mas ataques y justificar acciones tecnicas con datos consistentes."
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
