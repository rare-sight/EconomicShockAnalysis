# Economic Shock Analysis

A small Python pipeline that loads public economic indicators into SQLite and calculates pre/post-shock changes.

## Structure

- `data_collection/`: source-specific download and load scripts
- `processing/`: impact calculations
- `storage/`: SQLite schema
- `deploy/`: local database initialization
- `utils/`: shared configuration and database helpers

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m deploy.setup_db
```

Run collectors from the repository root so package imports resolve consistently:

```powershell
python -m data_collection.fetch_worldbank_gdp
python -m data_collection.fetch_ecb_exchange
python -m data_collection.fetch_oil_price
python -m data_collection.fetch_oecd_cpi
python -m processing.compute_impact
```

The FRED collector requires a `fred` section with `base_url` and `api_key` in `sources.yaml`.
