
import sqlite3
from pathlib import Path

database_path = Path(__file__).parent / "farmers.db"

connection = sqlite3.connect(database_path)

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS farmers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    location TEXT NOT NULL,
    farm_size REAL NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

connection.commit()
connection.close()

print("CultivaSense database created successfully!")
