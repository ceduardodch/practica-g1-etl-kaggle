from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


RAW_DIR = Path("data/raw")


def postgres_url() -> str:
    load_dotenv()
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ["POSTGRES_DB"]
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def to_snake_case(column: str) -> str:
    return (
        column.strip()
        .lower()
        .replace("/", "_")
        .replace("-", "_")
        .replace(" ", "_")
    )


def main() -> None:
    csv_path = RAW_DIR / "cybersecurity_attacks.csv"
    assets_path = RAW_DIR / "asset_inventory.csv"
    if not csv_path.exists() or not assets_path.exists():
        raise FileNotFoundError("Missing cybersecurity source files. Run scripts/download_data.py first.")

    alerts = pd.read_csv(csv_path)
    assets = pd.read_csv(assets_path)
    ip_to_machine = dict(zip(assets["ip_address"], assets["machine_id"], strict=False))

    alerts["machine_id"] = alerts["Destination IP Address"].map(ip_to_machine).fillna("SRV-UNTRACKED")
    alerts["alert_id"] = (
        alerts["Attack Type"].str.upper().str.replace(" ", "-", regex=False)
        + "-"
        + alerts["Protocol"].str.upper()
    )
    alerts = alerts.rename(columns={column: to_snake_case(column) for column in alerts.columns})

    engine = create_engine(postgres_url())
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS network_alerts"))

    alerts.to_sql("network_alerts", engine, if_exists="replace", index=False, chunksize=2500)

    with engine.begin() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM network_alerts")).scalar_one()
        avg_packet = conn.execute(text("SELECT ROUND(AVG(packet_length)::numeric, 2) FROM network_alerts")).scalar_one()

    print(f"loaded table network_alerts rows={count} avg_packet_length={avg_packet}")


if __name__ == "__main__":
    main()
