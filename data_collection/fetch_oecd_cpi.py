"""Load annual CPI observations from the configured OECD CSVs."""

from datetime import date

import pandas as pd

from utils.config import load_config
from utils.db import get_connection


def fetch_cpi_for_country(base_url, country_iso):
    data = pd.read_csv(f"{base_url}/{country_iso}.csv")
    data.columns = [column.lower() for column in data.columns]
    if not {"time", "value"}.issubset(data.columns):
        raise ValueError(f"CPI CSV for {country_iso} must contain time and value columns")

    return [
        (country_iso, date(int(year), 12, 31), float(value))
        for year, value in data[["time", "value"]].dropna().itertuples(index=False)
    ]


def main():
    config = load_config()
    records = []
    with get_connection() as connection:
        countries = [row[0] for row in connection.execute("SELECT iso_code FROM countries WHERE iso_code != 'GLOBAL'")]
        for country_iso in countries:
            try:
                records.extend(
                    fetch_cpi_for_country(config["oecd_cpi"]["base_url"], country_iso)
                )
            except (ValueError, OSError) as error:
                print(f"Skipping {country_iso}: {error}")

        connection.executemany(
            """
            INSERT INTO indicator_values (country_iso, indicator, period, value)
            VALUES (?, 'CPI', ?, ?)
            ON CONFLICT(country_iso, indicator, period) DO UPDATE SET value = excluded.value
            """,
            records,
        )

    print(f"Loaded {len(records)} CPI observations.")


if __name__ == "__main__":
    main()
