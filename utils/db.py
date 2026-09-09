from pathlib import Path
import sqlite3


DATABASE_PATH = Path(__file__).resolve().parents[1] / "economic_shock.db"


def get_connection(database_path=DATABASE_PATH):
    conn = sqlite3.connect(database_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
