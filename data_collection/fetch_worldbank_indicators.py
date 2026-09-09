"""Load annual economic indicators for the observatory from the World Bank API."""

import requests

from utils.config import load_config
from utils.db import get_connection


WORLD_BANK_INDICATORS = {
    "GDP_GROWTH": "NY.GDP.MKTP.KD.ZG",
    "INFLATION": "FP.CPI.TOTL.ZG",
    "UNEMPLOYMENT": "SL.UEM.TOTL.ZS",
    "EXCHANGE_RATE": "PA.NUS.FCRF",
    "FDI": "BX.KLT.DINV.CD.WD",
}
START_YEAR = 2017
END_YEAR = 2024


def fetch_indicator(base_url, country_iso, series_code):
    response = requests.get(
        f"{base_url}/country/{country_iso}/indicator/{series_code}",
        params={"format": "json", "per_page": 1000, "date": f"{START_YEAR}:{END_YEAR}"},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or len(payload) < 2:
        return []
    return [
        (country_iso, indicator, f"{row['date']}-12-31", float(row["value"]))
        for row in payload[1]
        if row.get("value") is not None
        for indicator, code in WORLD_BANK_INDICATORS.items()
        if code == series_code
    ]


def main():
    base_url = load_config()["world_bank"]["base_url"]
    with get_connection() as connection:
        countries = [
            row[0] for row in connection.execute(
                "SELECT iso_code FROM countries WHERE iso_code != 'GLOBAL'"
            )
        ]
        records = []
        for country_iso in countries:
            for indicator, series_code in WORLD_BANK_INDICATORS.items():
                try:
                    records.extend(fetch_indicator(base_url, country_iso, series_code))
                except requests.RequestException as error:
                    print(f"Skipping {country_iso}/{indicator}: {error}")
        connection.executemany(
            """INSERT INTO indicator_values (country_iso, indicator, period, value)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(country_iso, indicator, period) DO UPDATE SET value = excluded.value""",
            records,
        )
    print(f"Loaded {len(records)} annual World Bank observations.")


if __name__ == "__main__":
    main()
