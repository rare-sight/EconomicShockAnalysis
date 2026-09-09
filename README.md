# Economic Shock Analysis

A Python pipeline that downloads public economic indicators, stores them in SQLite, and calculates pre/post-shock changes.

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
.venv\Scripts\python.exe -m deploy.setup_db
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
.venv\Scripts\python.exe -m data_collection.fetch_worldbank_gdp
.venv\Scripts\python.exe -m data_collection.fetch_ecb_exchange
.venv\Scripts\python.exe -m data_collection.fetch_oil_price
.venv\Scripts\python.exe -m data_collection.fetch_oecd_cpi
.venv\Scripts\python.exe -m processing.compute_impact
```

The setup command creates `economic_shock.db`, seeds the countries and indicators, and loads the shocks from `data_collection\shocks.csv`.

FRED is optional. Its collector requires a `fred` section with `base_url` and `api_key` in `sources.yaml` before it can run.
