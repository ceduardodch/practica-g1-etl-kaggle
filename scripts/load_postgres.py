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


def main() -> None:
    csv_path = RAW_DIR / "olist_order_items_dataset.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing {csv_path}. Run scripts/download_data.py first.")

    df = pd.read_csv(csv_path)
    engine = create_engine(postgres_url())

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS order_items"))

    df.to_sql("order_items", engine, if_exists="replace", index=False, chunksize=5000)

    with engine.begin() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM order_items")).scalar_one()
        avg_price = conn.execute(text("SELECT ROUND(AVG(price)::numeric, 2) FROM order_items")).scalar_one()

    print(f"loaded table order_items rows={count} avg_price={avg_price}")


if __name__ == "__main__":
    main()

