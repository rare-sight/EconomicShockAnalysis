"""Export analysis tables to CSV files for Power BI."""

import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

from utils.config import PROJECT_ROOT


DATABASE_PATH = PROJECT_ROOT / "economic_shock.db"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "power_bi"
LEGACY_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "shock_impacts.csv"

IMPACTS_QUERY = """
SELECT shock_impacts.impact_id, shock_impacts.shock_id, shocks.name AS shock,
       shocks.start_date AS shock_start_date, shocks.end_date AS shock_end_date,
       shock_impacts.country_iso, countries.name AS country,
       shock_impacts.indicator AS indicator_code,
       indicators.display_name AS indicator, indicators.description AS indicator_description,
       indicators.unit AS indicator_unit, indicators.frequency, indicators.source,
       shock_impacts.pre_value, shock_impacts.shock_value, shock_impacts.post_value,
       shock_impacts.absolute_change, shock_impacts.pct_change, shock_impacts.change_type
FROM shock_impacts
JOIN shocks ON shocks.shock_id = shock_impacts.shock_id
JOIN countries ON countries.iso_code = shock_impacts.country_iso
JOIN indicators ON indicators.indicator_code = shock_impacts.indicator
ORDER BY shocks.start_date, shock_impacts.country_iso, indicators.display_name
"""

INDICATOR_VALUES_QUERY = """
SELECT indicator_values.country_iso, countries.name AS country,
       indicator_values.indicator AS indicator_code,
       indicators.display_name AS indicator, indicators.unit AS indicator_unit,
       indicators.frequency, indicators.source, indicators.change_type,
       indicator_values.period, indicator_values.value
FROM indicator_values
JOIN countries ON countries.iso_code = indicator_values.country_iso
JOIN indicators ON indicators.indicator_code = indicator_values.indicator
ORDER BY indicator_values.period, indicator_values.country_iso, indicator_values.indicator
"""

TABLE_EXPORTS = {
    "dim_countries.csv": "SELECT iso_code AS country_iso, name AS country FROM countries ORDER BY iso_code",
    "dim_indicators.csv": "SELECT indicator_code, display_name AS indicator, description, unit AS indicator_unit, frequency, source, change_type FROM indicators ORDER BY indicator_code",
    "dim_shocks.csv": "SELECT shock_id, name AS shock, start_date, end_date, description, baseline_start_year, baseline_end_year, shock_year, recovery_start_year, recovery_end_year FROM shocks ORDER BY start_date",
    "fact_indicator_values.csv": INDICATOR_VALUES_QUERY,
    "fact_shock_impacts.csv": IMPACTS_QUERY,
}


def create_summary_exports(impacts):
    country_impacts = impacts[impacts["country_iso"] != "GLOBAL"].copy()
    summary = country_impacts.groupby(
        ["shock", "indicator_code", "indicator", "indicator_unit", "change_type"], as_index=False
    ).agg(
        country_count=("country_iso", "nunique"),
        average_pre_value=("pre_value", "mean"),
        average_shock_value=("shock_value", "mean"),
        average_post_value=("post_value", "mean"),
        average_absolute_change=("absolute_change", "mean"),
        average_pct_change=("pct_change", "mean"),
    )
    recovery = country_impacts.groupby(["shock", "country_iso", "country", "change_type"], as_index=False).agg(
        indicator_count=("indicator_code", "nunique"),
        unweighted_average_absolute_change=("absolute_change", "mean"),
        unweighted_average_pct_change=("pct_change", "mean"),
    )
    return summary, recovery


def create_chart(impacts):
    impacts = impacts[impacts["country_iso"] != "GLOBAL"].copy()
    indicators = impacts["indicator"].drop_duplicates().tolist()
    figure, axes = plt.subplots(len(indicators), 1, figsize=(11, 3.5 * len(indicators)))
    for axis, indicator in zip(axes, indicators):
        subset = impacts[impacts["indicator"] == indicator].sort_values("country")
        change_column = "absolute_change" if subset["change_type"].iloc[0] == "percentage_points" else "pct_change"
        label = "Percentage-point change" if change_column == "absolute_change" else "Percent change"
        axis.bar(subset["country"], subset[change_column], color="#2f6f9f")
        axis.axhline(0, color="black", linewidth=0.8)
        axis.set_title(f"COVID-19 recovery change: {indicator}")
        axis.set_ylabel(label)
        axis.tick_params(axis="x", rotation=20)
    figure.tight_layout()
    figure.savefig(OUTPUT_DIR / "shock_impact_by_indicator.png", dpi=150)
    plt.close(figure)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as connection:
        exports = {
            filename: pd.read_sql_query(query, connection)
            for filename, query in TABLE_EXPORTS.items()
        }

    if exports["fact_shock_impacts.csv"].empty:
        raise RuntimeError("No impact results found. Run processing.compute_impact first.")

    for filename, dataframe in exports.items():
        dataframe.to_csv(OUTPUT_DIR / filename, index=False)
        print(f"Exported {len(dataframe)} rows to {OUTPUT_DIR / filename}")

    exports["fact_shock_impacts.csv"].to_csv(LEGACY_OUTPUT_PATH, index=False)
    print(f"Exported compatibility impact file to {LEGACY_OUTPUT_PATH}")

    summary, recovery = create_summary_exports(exports["fact_shock_impacts.csv"])
    summary.to_csv(OUTPUT_DIR / "summary_impact_by_shock_indicator.csv", index=False)
    recovery.to_csv(OUTPUT_DIR / "summary_country_recovery.csv", index=False)
    create_chart(exports["fact_shock_impacts.csv"])
    print(f"Exported {len(summary)} summary rows and {len(recovery)} recovery rows.")


if __name__ == "__main__":
    main()
