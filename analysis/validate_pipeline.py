"""Print a concise validation report for the generated observatory dataset."""

from utils.db import get_connection
from utils.config import PROJECT_ROOT
from utils.validation import validate_data, validation_summary


def main():
    with get_connection() as connection:
        validate_data(connection)
        report = validation_summary(connection)
        periods = connection.execute(
            "SELECT name, baseline_start_year, baseline_end_year, shock_year, recovery_start_year, recovery_end_year FROM shocks"
        ).fetchall()
        samples = connection.execute(
            """SELECT c.name, i.display_name, s.name, si.pre_value, si.shock_value,
                      si.post_value, si.absolute_change, si.pct_change, si.change_type
               FROM shock_impacts si JOIN countries c ON c.iso_code = si.country_iso
               JOIN indicators i ON i.indicator_code = si.indicator
               JOIN shocks s ON s.shock_id = si.shock_id
               ORDER BY c.name, i.display_name LIMIT 5"""
        ).fetchall()
    lines = [
        "VALIDATION PASSED",
        f"Countries: {report['countries']}; indicators: {report['indicators']}",
        f"Observations: {report['observations']}; date range: {report['date_range'][0]} to {report['date_range'][1]}",
        f"Missing values: {report['missing_values']}; duplicate rows: {report['duplicate_rows']}",
    ]
    for period in periods:
        lines.append(f"Shock period: {period[0]} — baseline {period[1]}-{period[2]}, shock {period[3]}, recovery {period[4]}-{period[5]}")
    lines.append("Sample impacts:")
    for sample in samples:
        lines.append(str(sample))
    output_path = PROJECT_ROOT / "outputs" / "power_bi" / "validation_report.txt"
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"Saved validation report to {output_path}")


if __name__ == "__main__":
    main()
