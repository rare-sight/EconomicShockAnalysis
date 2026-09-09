# Economic Shock Analysis

A Python pipeline that downloads public economic indicators, stores them in SQLite, and calculates pre/post-shock changes.

The `analysis` package exports the calculated results and raw economic data as
Power BI-ready CSV files.

## Prerequisites

- Windows with Python 3.11 or newer
- Internet access for the World Bank, ECB, oil-price, and OECD downloads
- PowerShell or Command Prompt
- No PostgreSQL server, database, username, or API key is required for the default collectors

## First-time setup

Open a terminal in the repository root (`D:\EconomicShockAnalysis`) and run:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m deploy.setup_db --reset
```

Using `.venv\Scripts\python.exe` avoids accidentally using a different Python interpreter. In PowerShell, you can activate the environment first:

```powershell
.venv\Scripts\Activate.ps1
```

In Command Prompt, use:

```cmd
.venv\Scripts\activate.bat
```

## Run the pipeline

Always run these commands from the repository root. Use `-m`; do not run a file directly such as `python data_collection\fetch_worldbank_gdp.py`, because the shared `utils` package will not be found.

```powershell
.venv\Scripts\python.exe -m data_collection.fetch_worldbank_indicators
.venv\Scripts\python.exe -m data_collection.fetch_oil_price
.venv\Scripts\python.exe -m processing.compute_impact
.venv\Scripts\python.exe -m analysis.visualize
.venv\Scripts\python.exe -m analysis.validate_pipeline
```

The setup command recreates the generated `economic_shock.db`, seeds the five
countries and indicator metadata, and loads the documented shock methodology
from `data_collection\shocks.csv`.

The World Bank collector loads annual GDP growth, consumer-price inflation,
unemployment, official exchange rates, and FDI for 2017–2024. Inflation is a
rate, not a CPI index; it is therefore reported as a percentage-point change.

The export command creates the following files in `outputs\power_bi`:

- `fact_shock_impacts.csv` — calculated pre/post-shock changes; use this for the main analysis.
- `fact_indicator_values.csv` — every raw source observation with its date, country and indicator.
- `dim_countries.csv`, `dim_indicators.csv`, `dim_shocks.csv` — optional lookup tables for a Power BI star schema.
- `summary_impact_by_shock_indicator.csv` — a separate country-average summary, not a replacement for detailed results.
- `summary_country_recovery.csv` — unweighted country recovery metrics, separated by change type.
- `shock_impact_by_indicator.png` — one panel per indicator, so percentage-point and percent changes are never plotted on one axis.
- `validation_report.txt` — source-data and calculation validation results.

`outputs\shock_impacts.csv` is also created for compatibility; it contains the
same detailed rows as `fact_shock_impacts.csv`.

In Power BI Desktop, choose **Get data → Text/CSV** and load the CSV files from
`outputs\power_bi`. Set `period`, `shock_start_date`, and `shock_end_date` to
the Date data type; set the averages, values, and `pct_change` to Decimal Number.
For a simple report, `fact_shock_impacts.csv` is self-describing and can be used
on its own. For a model with relationships, use the `*_id`/`*_code` columns to
link the fact and dimension files.

FRED is optional. Its collector requires a `fred` section with `base_url` and `api_key` in `sources.yaml` before it can run.
