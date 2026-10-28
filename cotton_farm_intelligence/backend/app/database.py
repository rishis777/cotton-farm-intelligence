"""
Database module for Cotton Farm Intelligence Dashboard.
Uses SQLite for persistent storage of saved farms and analysis history.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "cotton_farms.db"

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite schema if tables do not exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Saved Farms Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_farms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                taluka TEXT,
                notes TEXT,
                latest_suitability_category TEXT,
                latest_suitability_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Analysis History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farm_id INTEGER,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                suitability_category TEXT NOT NULL,
                suitability_score REAL,
                evidence_json TEXT NOT NULL,
                weather_json TEXT,
                soil_json TEXT,
                FOREIGN KEY (farm_id) REFERENCES saved_farms (id) ON DELETE SET NULL
            )
        """)
        conn.commit()

# Seed default Dhule taluka farms if database is empty
def seed_default_farms_if_empty():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM saved_farms")
        count = cursor.fetchone()["count"]
        if count == 0:
            default_farms = [
                ("Dhule Agricultural Research Station", 20.9042, 74.7749, "Dhule", "Benchmark cotton monitoring plot, deep black soil (Vertisol)"),
                ("Shirpur Taluka Farm", 21.3500, 74.8800, "Shirpur", "Canal and well irrigated cotton cultivation area"),
                ("Sindkheda Agro Demonstration Center", 21.2667, 74.7500, "Sindkheda", "Tapi river basin high-productivity cotton belt"),
                ("Sakri Rainfed Cotton Field", 20.9333, 74.3167, "Sakri", "Hilly rainfed Kharif cotton tract")
            ]
            for name, lat, lon, taluka, notes in default_farms:
                cursor.execute("""
                    INSERT INTO saved_farms (name, latitude, longitude, taluka, notes, latest_suitability_category, latest_suitability_score)
                    VALUES (?, ?, ?, ?, ?, 'Potentially suitable with constraints', 74.5)
                """, (name, lat, lon, taluka, notes))
            conn.commit()

# Initialize tables immediately upon module import
init_db()
seed_default_farms_if_empty()
