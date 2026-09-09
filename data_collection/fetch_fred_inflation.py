"""Load monthly inflation observations from FRED when configured."""

from datetime import date

import requests

from utils.config import load_config
from utils.db import get_connection


def fetch_series(config, series_id):
    response = requests.get(
        config["base_url"],
        params={
            "series_id": series_id,
            "api_key": config["api_key"],
            "observation_start": "2000-01-01",
            "output_type": 1,
            "file_type": "json",
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("observations", [])


def main():
    config = load_config().get("fred")
    if not config:
        raise RuntimeError("Add a fred section to sources.yaml before running this script")

    with get_connection() as connection:
        series_ids = [
            row[0]
            for row in connection.execute(
                "SELECT indicator_code FROM indicators WHERE indicator_code LIKE 'CPI%'"
            )
        ]
        records = []
        for series_id in series_ids:
            for observation in fetch_series(config, series_id):
                if observation["value"] == ".":
                    continue
                year, month, day = map(int, observation["date"].split("-"))
                records.append(
                    (series_id.split("_")[0], date(year, month, day), float(observation["value"]))
                )

        connection.executemany(
            """
            INSERT INTO indicator_values (country_iso, indicator, period, value)
            VALUES (?, 'INFLATION', ?, ?)
            ON CONFLICT(country_iso, indicator, period) DO UPDATE SET value = excluded.value
            """,
            records,
        )

    print(f"Loaded {len(records)} inflation observations.")


if __name__ == "__main__":
    main()
