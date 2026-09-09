"""Calculate annual baseline, shock-year, and recovery impacts by country."""

from utils.db import get_connection
from utils.validation import validate_data


def main():
    with get_connection() as connection:
        validate_data(connection)
        shocks = connection.execute(
            """SELECT shock_id, name, baseline_start_year, baseline_end_year,
                      shock_year, recovery_start_year, recovery_end_year
               FROM shocks"""
        ).fetchall()
        for shock_id, name, baseline_start, baseline_end, shock_year, recovery_start, recovery_end in shocks:

            connection.execute(
                "DELETE FROM shock_impacts WHERE shock_id = ?",
                (shock_id,),
            )
            connection.execute(
                """
                INSERT OR REPLACE INTO shock_impacts
                    (shock_id, country_iso, indicator, pre_value, shock_value, post_value,
                     absolute_change, pct_change, change_type)
                WITH pre AS (
                    SELECT country_iso, indicator, AVG(value) AS average
                    FROM indicator_values
                    WHERE CAST(substr(period, 1, 4) AS INTEGER) BETWEEN ? AND ?
                    GROUP BY country_iso, indicator
                ), shock AS (
                    SELECT country_iso, indicator, AVG(value) AS value
                    FROM indicator_values
                    WHERE CAST(substr(period, 1, 4) AS INTEGER) = ?
                    GROUP BY country_iso, indicator
                ), post AS (
                    SELECT country_iso, indicator, AVG(value) AS average
                    FROM indicator_values
                    WHERE CAST(substr(period, 1, 4) AS INTEGER) BETWEEN ? AND ?
                    GROUP BY country_iso, indicator
                )
                SELECT ?, pre.country_iso, pre.indicator, pre.average, shock.value, post.average,
                       post.average - pre.average,
                       CASE WHEN indicators.change_type = 'percent' AND pre.average != 0
                            THEN (post.average - pre.average) / pre.average * 100 END,
                       indicators.change_type
                FROM pre
                JOIN shock USING (country_iso, indicator)
                JOIN post USING (country_iso, indicator)
                JOIN indicators ON indicators.indicator_code = pre.indicator
                """,
                (
                    baseline_start, baseline_end, shock_year, recovery_start, recovery_end,
                    shock_id,
                ),
            )
            print(f"Calculated impact for '{name}' (ID {shock_id}).")

    print("Shock impacts calculated.")


if __name__ == "__main__":
    main()
