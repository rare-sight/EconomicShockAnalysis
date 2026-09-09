"""Calculate pre- and post-shock averages for each series."""

from datetime import date, timedelta

from utils.db import get_connection


PRE_PERIOD_QUARTERS = 4
POST_PERIOD_QUARTERS = 4
DAYS_PER_QUARTER = 91


def period_offset(start, quarters):
    return start - timedelta(days=quarters * DAYS_PER_QUARTER)


def main():
    with get_connection() as connection:
        shocks = connection.execute(
            "SELECT shock_id, name, start_date FROM shocks"
        ).fetchall()
        for shock_id, name, start_date_text in shocks:
            start_date = date.fromisoformat(start_date_text)
            pre_start = period_offset(start_date, PRE_PERIOD_QUARTERS)
            pre_end = start_date - timedelta(days=1)
            post_end = start_date + timedelta(days=POST_PERIOD_QUARTERS * DAYS_PER_QUARTER - 1)

            connection.execute(
                """
                INSERT OR REPLACE INTO shock_impacts
                    (shock_id, country_iso, indicator, pre_average, post_average, pct_change)
                WITH pre AS (
                    SELECT country_iso, indicator, AVG(value) AS average
                    FROM indicator_values
                    WHERE period BETWEEN ? AND ?
                    GROUP BY country_iso, indicator
                ), post AS (
                    SELECT country_iso, indicator, AVG(value) AS average
                    FROM indicator_values
                    WHERE period BETWEEN ? AND ?
                    GROUP BY country_iso, indicator
                )
                SELECT ?, pre.country_iso, pre.indicator, pre.average, post.average,
                       CASE WHEN pre.average = 0 THEN NULL
                            ELSE (post.average - pre.average) / pre.average * 100 END
                FROM pre
                JOIN post USING (country_iso, indicator)
                """,
                (pre_start, pre_end, start_date, post_end, shock_id),
            )
            print(f"Calculated impact for '{name}' (ID {shock_id}).")

    print("Shock impacts calculated.")


if __name__ == "__main__":
    main()
