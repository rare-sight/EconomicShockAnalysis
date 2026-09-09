"""Initialize the local SQLite database."""

import csv

from utils.config import PROJECT_ROOT
from utils.db import get_connection


SCHEMA_PATH = PROJECT_ROOT / "storage" / "schema_sqlite.sql"
SHOCKS_PATH = PROJECT_ROOT / "data_collection" / "shocks.csv"

INDICATORS = [
    ("GDP", "GDP (current US$)", "USD"),
    ("INFLATION", "Consumer Price Index (annual %)", "%"),
    ("EXCHANGE_EUR", "Exchange rate to EUR", "Rate"),
    ("OIL_BRN", "Brent crude oil price", "USD per barrel"),
    ("CPI", "CPI (annual %)", "%"),
]

COUNTRIES = [
    ("GLOBAL", "Global"),
    ("USA", "United States"),
    ("GBR", "United Kingdom"),
    ("JPN", "Japan"),
    ("DEU", "Germany"),
    ("IND", "India"),
    ("RUS", "Russia"),
    ("CHN", "China"),
]


def main():
    with get_connection() as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        connection.executemany(
            "INSERT OR IGNORE INTO indicators (indicator_code, display_name, unit) VALUES (?, ?, ?)",
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
                    row["description"],
                )
                for row in csv.DictReader(file)
            ]
        connection.executemany(
            """
            INSERT OR IGNORE INTO shocks
                (shock_id, name, start_date, end_date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            shocks,
        )

    print("SQLite database initialized.")


if __name__ == "__main__":
    main()
