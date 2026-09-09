"""Load daily Brent crude oil prices from the configured CSV."""

import pandas as pd

from utils.config import load_config
from utils.db import get_connection


START_DATE = "2017-01-01"
END_DATE = "2024-12-31"


def main():
    config = load_config()
    data = pd.read_csv(config["oil_price"]["csv_url"])
    data.columns = [column.strip().lower() for column in data.columns]
    if not {"date", "price"}.issubset(data.columns):
        raise ValueError("Oil CSV must contain date and price columns")

    data["date"] = pd.to_datetime(data["date"])
    data = data[data["date"].between(START_DATE, END_DATE)]
    records = [
        (period.date().isoformat(), float(price))
        for period, price in data[["date", "price"]].dropna().itertuples(index=False)
    ]

    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO indicator_values (country_iso, indicator, period, value)
            VALUES ('GLOBAL', 'OIL_BRENT', ?, ?)
            ON CONFLICT(country_iso, indicator, period) DO UPDATE SET value = excluded.value
            """,
            records,
        )

    print(f"Loaded {len(records)} oil-price observations.")


if __name__ == "__main__":
    main()
