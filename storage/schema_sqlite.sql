-- schema_sqlite.sql
-- SQLite‑compatible schema for Economic Shock Impact Analysis

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS countries (
    iso_code TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shocks (
    shock_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS indicators (
    indicator_code TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    unit TEXT
);

CREATE TABLE IF NOT EXISTS indicator_values (
    country_iso TEXT NOT NULL,
    indicator TEXT NOT NULL,
    period DATE NOT NULL,
    value REAL,
    PRIMARY KEY (country_iso, indicator, period),
    FOREIGN KEY (country_iso) REFERENCES countries(iso_code),
    FOREIGN KEY (indicator) REFERENCES indicators(indicator_code)
);

CREATE TABLE IF NOT EXISTS shock_impacts (
    impact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shock_id INTEGER NOT NULL,
    country_iso TEXT NOT NULL,
    indicator TEXT NOT NULL,
    pre_average REAL,
    post_average REAL,
    pct_change REAL,
    calc_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shock_id) REFERENCES shocks(shock_id),
    FOREIGN KEY (country_iso) REFERENCES countries(iso_code),
    FOREIGN KEY (indicator) REFERENCES indicators(indicator_code)
);
