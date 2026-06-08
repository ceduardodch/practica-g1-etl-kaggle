from pathlib import Path
import json
import shutil

import kagglehub
import pandas as pd


DATASET = "olistbr/brazilian-ecommerce"
RAW_DIR = Path("data/raw")

FILES_TO_COPY = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "product_category_name_translation.csv",
]


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dataset_path = Path(kagglehub.dataset_download(DATASET))

    for filename in FILES_TO_COPY:
        source = dataset_path / filename
        target = RAW_DIR / filename
        shutil.copy2(source, target)
        print(f"copied {filename} -> {target}")

    translations = pd.read_csv(RAW_DIR / "product_category_name_translation.csv")
    translations["category_name_length"] = translations["product_category_name"].str.len()
    translations["english_name_length"] = translations["product_category_name_english"].str.len()
    translations["first_letter"] = translations["product_category_name_english"].str[0].str.upper()

    records = translations.to_dict(orient="records")
    (RAW_DIR / "product_categories.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"created {RAW_DIR / 'product_categories.json'} with {len(records)} rows")


if __name__ == "__main__":
    main()

