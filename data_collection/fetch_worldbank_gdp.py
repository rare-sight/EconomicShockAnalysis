"""Load annual GDP observations from the World Bank API."""

import requests

from utils.config import load_config
from utils.db import get_connection


INDICATOR = "NY.GDP.MKTP.CD"


def fetch_gdp_for_country(base_url, iso_code):
    url = f"{base_url}/countries/{iso_code}/indicators/{INDICATOR}"
    response = requests.get(url, params={"format": "json", "per_page": 1000}, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or len(payload) < 2:
        return []

    return [
        (iso_code, f"{entry['date']}-12-31", float(entry["value"]))
        for entry in payload[1]
        if entry.get("value") is not None
    ]


def main():
    config = load_config()
    with get_connection() as connection:
        countries = [row[0] for row in connection.execute("SELECT iso_code FROM countries")]
        records = []
        for country_iso in countries:
            try:
                records.extend(
                    fetch_gdp_for_country(config["world_bank"]["base_url"], country_iso)
                )
            except requests.RequestException as error:
                print(f"Skipping {country_iso}: {error}")

        connection.executemany(
            """
            INSERT INTO indicator_values (country_iso, indicator, period, value)
            VALUES (?, 'GDP', ?, ?)
            ON CONFLICT(country_iso, indicator, period) DO UPDATE SET value = excluded.value
            """,
            records,
        )

    print(f"Loaded {len(records)} GDP observations.")


if __name__ == "__main__":
    main()
