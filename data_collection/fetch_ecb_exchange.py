"""Load daily EUR exchange rates from the configured ECB CSV."""

import pandas as pd

from utils.config import load_config
from utils.db import get_connection


ISO_TO_CURRENCY = {
    "USA": "USD",
    "GBR": "GBP",
    "JPN": "JPY",
    "DEU": "EUR",
    "IND": "INR",
    "CHN": "CNY",
    "CAN": "CAD",
    "AUS": "AUD",
    "NZL": "NZD",
    "BRA": "BRL",
    "RUS": "RUB",
}


def main():
    config = load_config()
    data = pd.read_csv(config["ecb"]["exchange_rates_url"])
    data["Date"] = pd.to_datetime(data["Date"]).dt.date

    records = []
    for country_iso, currency in ISO_TO_CURRENCY.items():
        if currency not in data.columns:
            continue
        for period, value in data[["Date", currency]].dropna().itertuples(index=False):
            records.append((country_iso, period, float(value)))

    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO indicator_values (country_iso, indicator, period, value)
            VALUES (?, 'EXCHANGE_EUR', ?, ?)
            ON CONFLICT(country_iso, indicator, period) DO UPDATE SET value = excluded.value
            """,
            records,
        )

    print(f"Loaded {len(records)} exchange-rate observations.")


if __name__ == "__main__":
    main()
