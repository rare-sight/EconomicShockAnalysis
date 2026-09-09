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
    description TEXT,
    baseline_start_year INTEGER NOT NULL,
    baseline_end_year INTEGER NOT NULL,
    shock_year INTEGER NOT NULL,
    recovery_start_year INTEGER NOT NULL,
    recovery_end_year INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS indicators (
    indicator_code TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    description TEXT NOT NULL,
    unit TEXT NOT NULL,
    frequency TEXT NOT NULL,
    source TEXT NOT NULL,
    change_type TEXT NOT NULL CHECK (change_type IN ('percentage_points', 'percent'))
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
    pre_value REAL,
    shock_value REAL,
    post_value REAL,
    absolute_change REAL,
    pct_change REAL,
    change_type TEXT NOT NULL,
    calc_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shock_id) REFERENCES shocks(shock_id),
    FOREIGN KEY (country_iso) REFERENCES countries(iso_code),
    FOREIGN KEY (indicator) REFERENCES indicators(indicator_code)
);
