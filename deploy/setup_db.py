"""Initialize the local SQLite database."""

import csv
import argparse

from utils.config import PROJECT_ROOT
from utils.db import get_connection


SCHEMA_PATH = PROJECT_ROOT / "storage" / "schema_sqlite.sql"
SHOCKS_PATH = PROJECT_ROOT / "data_collection" / "shocks.csv"

INDICATORS = [
    ("GDP_GROWTH", "GDP Growth", "Annual real GDP growth rate.", "%", "annual", "World Bank (NY.GDP.MKTP.KD.ZG)", "percentage_points"),
    ("INFLATION", "Inflation, consumer prices", "Annual consumer-price inflation rate; not a CPI index.", "%", "annual", "World Bank (FP.CPI.TOTL.ZG)", "percentage_points"),
    ("UNEMPLOYMENT", "Unemployment, total", "Share of the total labour force that is unemployed.", "%", "annual", "World Bank (SL.UEM.TOTL.ZS)", "percentage_points"),
    ("EXCHANGE_RATE", "Official exchange rate", "Annual average local currency units per US dollar.", "LCU per USD", "annual", "World Bank (PA.NUS.FCRF)", "percent"),
    ("FDI", "Foreign direct investment, net inflows", "Net inward foreign direct investment flows in current US dollars.", "current USD", "annual", "World Bank (BX.KLT.DINV.CD.WD)", "percent"),
    ("OIL_BRENT", "Brent crude oil price", "Global Brent crude oil market price; not a country-level indicator.", "USD per barrel", "daily", "Our World in Data / EIA Brent series", "percent"),
]

COUNTRIES = [
    ("GLOBAL", "Global market"),
    ("USA", "United States"),
    ("GBR", "United Kingdom"),
    ("JPN", "Japan"),
    ("DEU", "Germany"),
    ("IND", "India"),
]


def main(reset=False):
    database_path = PROJECT_ROOT / "economic_shock.db"
    if reset and database_path.exists():
        database_path.unlink()
    with get_connection() as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        connection.executemany(
            """INSERT INTO indicators
               (indicator_code, display_name, description, unit, frequency, source, change_type)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            INDICATORS,
        )
        connection.executemany(
            "INSERT OR IGNORE INTO countries (iso_code, name) VALUES (?, ?)",
            COUNTRIES,
        )
        with SHOCKS_PATH.open(newline="", encoding="utf-8") as file:
            shocks = [
                (
                    int(row["shock_id"]),
                    row["name"],
                    row["start_date"],
                    row["end_date"] or None,
                    row["description"], int(row["baseline_start_year"]), int(row["baseline_end_year"]),
                    int(row["shock_year"]), int(row["recovery_start_year"]), int(row["recovery_end_year"]),
                )
                for row in csv.DictReader(file)
            ]
        connection.executemany(
            """
            INSERT INTO shocks
            (shock_id, name, start_date, end_date, description, baseline_start_year,
             baseline_end_year, shock_year, recovery_start_year, recovery_end_year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            shocks,
        )

    print("SQLite database initialized.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize the observatory database.")
    parser.add_argument("--reset", action="store_true", help="Recreate the generated database from scratch.")
    main(reset=parser.parse_args().reset)
