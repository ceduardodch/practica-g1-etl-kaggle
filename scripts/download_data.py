from pathlib import Path
import json

import kagglehub
import pandas as pd


DATASET = "teamincribo/cyber-security-attacks"
RAW_DIR = Path("data/raw")


def build_asset_inventory(alerts: pd.DataFrame) -> pd.DataFrame:
    assets = (
        alerts[
            [
                "Destination IP Address",
                "Device Information",
                "Network Segment",
                "Log Source",
                "Severity Level",
            ]
        ]
        .drop_duplicates(subset=["Destination IP Address"])
        .head(250)
        .reset_index(drop=True)
        .copy()
    )
    assets.insert(0, "machine_id", [f"SRV-{idx + 1:04d}" for idx in range(len(assets))])
    assets = assets.rename(
        columns={
            "Destination IP Address": "ip_address",
            "Device Information": "device_information",
            "Network Segment": "network_segment",
            "Log Source": "log_source",
            "Severity Level": "criticality",
        }
    )
    assets["server_name"] = assets["machine_id"].str.replace("SRV-", "soc-node-", regex=False)
    assets["department"] = assets["network_segment"].map(
        {
            "Segment A": "Tecnologia",
            "Segment B": "Finanzas",
            "Segment C": "Operaciones",
        }
    ).fillna("Infraestructura")
    assets["operating_system"] = assets["device_information"].str.extract(
        r"(Windows|Linux|Mac OS X|Android|iOS)", expand=False
    ).fillna("Linux")
    return assets[
        [
            "machine_id",
            "server_name",
            "operating_system",
            "department",
            "ip_address",
            "network_segment",
            "criticality",
            "log_source",
        ]
    ]


def build_vulnerability_catalog(alerts: pd.DataFrame) -> list[dict]:
    severity_base = {"Low": 3.8, "Medium": 6.4, "High": 8.7}
    catalog = []
    grouped = alerts.groupby(["Attack Type", "Protocol", "Severity Level"], dropna=False)
    for idx, ((attack_type, protocol, severity), group) in enumerate(grouped, 1):
        attack_text = str(attack_type).replace(" ", "-").upper()
        protocol_text = str(protocol).upper()
        cvss = min(10.0, severity_base.get(str(severity), 5.5) + min(group["Anomaly Scores"].mean() / 100, 1.0))
        catalog.append(
            {
                "alert_id": f"ALRT-{idx:03d}",
                "attack_type": attack_type,
                "protocol": protocol,
                "severity_level": severity,
                "vulnerability_name": f"{attack_type} exposure over {protocol_text}",
                "cve_code": f"CVE-2024-{idx:04d}",
                "cvss_score": round(cvss, 2),
                "remediation_action": f"Revisar reglas IDS/IPS, endurecer {protocol_text} y priorizar parches para {attack_text}.",
            }
        )
    return catalog


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dataset_path = Path(kagglehub.dataset_download(DATASET))
    source = dataset_path / "cybersecurity_attacks.csv"

    alerts = pd.read_csv(source)
    alerts = alerts.head(10000).copy()
    alerts.to_csv(RAW_DIR / "cybersecurity_attacks.csv", index=False)

    asset_inventory = build_asset_inventory(alerts)
    asset_inventory.to_csv(RAW_DIR / "asset_inventory.csv", index=False)

    vulnerability_catalog = build_vulnerability_catalog(alerts)
    (RAW_DIR / "vulnerability_catalog.json").write_text(
        json.dumps(vulnerability_catalog, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"copied {len(alerts)} alert rows -> {RAW_DIR / 'cybersecurity_attacks.csv'}")
    print(f"created {len(asset_inventory)} assets -> {RAW_DIR / 'asset_inventory.csv'}")
    print(f"created {len(vulnerability_catalog)} vulnerabilities -> {RAW_DIR / 'vulnerability_catalog.json'}")


if __name__ == "__main__":
    main()
