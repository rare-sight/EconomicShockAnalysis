"""Validation checks run before impact calculation and export."""

from datetime import date


def validate_data(connection):
    errors = []
    duplicate_rows = connection.execute(
        """SELECT country_iso, indicator, period, COUNT(*) FROM indicator_values
           GROUP BY country_iso, indicator, period HAVING COUNT(*) > 1"""
    ).fetchall()
    if duplicate_rows:
        errors.append(f"Duplicate country/indicator/period rows: {duplicate_rows[:3]}")

    invalid_references = connection.execute(
        """SELECT COUNT(*) FROM indicator_values v
           LEFT JOIN countries c ON c.iso_code = v.country_iso
           LEFT JOIN indicators i ON i.indicator_code = v.indicator
           WHERE c.iso_code IS NULL OR i.indicator_code IS NULL"""
    ).fetchone()[0]
    if invalid_references:
        errors.append(f"Rows with invalid country or indicator codes: {invalid_references}")

    rows = connection.execute(
        """SELECT v.country_iso, v.indicator, v.period, v.value, i.frequency
           FROM indicator_values v JOIN indicators i ON i.indicator_code = v.indicator"""
    ).fetchall()
    if not rows:
        errors.append("No indicator observations were loaded.")
    for country, indicator, period, value, frequency in rows:
        if value is None:
            errors.append(f"Missing value for {country}/{indicator}/{period}")
            continue
        try:
            parsed = date.fromisoformat(period)
        except ValueError:
            errors.append(f"Invalid ISO date for {country}/{indicator}: {period}")
            continue
        if frequency == "annual" and (parsed.month, parsed.day) != (12, 31):
            errors.append(f"Annual series {country}/{indicator} has non-year-end period {period}")
        if indicator == "UNEMPLOYMENT" and not 0 <= value <= 100:
            errors.append(f"Impossible unemployment value for {country}/{period}: {value}")
        if indicator in {"GDP_GROWTH", "INFLATION"} and not -100 <= value <= 100:
            errors.append(f"Implausible annual rate for {country}/{indicator}/{period}: {value}")
        if indicator in {"EXCHANGE_RATE", "OIL_BRENT"} and value <= 0:
            errors.append(f"Non-positive level for {country}/{indicator}/{period}: {value}")

    required_annual = connection.execute(
        """SELECT c.iso_code, i.indicator_code
           FROM countries c CROSS JOIN indicators i
           WHERE c.iso_code != 'GLOBAL' AND i.frequency = 'annual'
           EXCEPT
           SELECT country_iso, indicator FROM indicator_values
           WHERE period BETWEEN '2017-01-01' AND '2024-12-31'"""
    ).fetchall()
    if required_annual:
        errors.append(f"Missing required annual series: {required_annual[:5]}")
    if errors:
        raise ValueError("Data validation failed:\n- " + "\n- ".join(errors[:20]))


def validation_summary(connection):
    return {
        "countries": connection.execute("SELECT COUNT(*) FROM countries WHERE iso_code != 'GLOBAL'").fetchone()[0],
        "indicators": connection.execute("SELECT COUNT(*) FROM indicators").fetchone()[0],
        "observations": connection.execute("SELECT COUNT(*) FROM indicator_values").fetchone()[0],
        "missing_values": connection.execute("SELECT COUNT(*) FROM indicator_values WHERE value IS NULL").fetchone()[0],
        "duplicate_rows": connection.execute("SELECT COUNT(*) FROM (SELECT 1 FROM indicator_values GROUP BY country_iso, indicator, period HAVING COUNT(*) > 1)").fetchone()[0],
        "date_range": connection.execute("SELECT MIN(period), MAX(period) FROM indicator_values").fetchone(),
    }
