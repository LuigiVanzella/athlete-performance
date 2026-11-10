
import os
import sqlite3
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

API_KEY = os.getenv("INTERVALS_API_KEY")
BASE_URL = "https://intervals.icu/api/v1"

response = requests.get(
    f"{BASE_URL}/athlete/0/wellness",
    auth=HTTPBasicAuth("API_KEY", API_KEY),
    params={
        "oldest": "2026-10-01",
        "newest": "2026-11-09"
    },
    timeout=30
)

response.raise_for_status()
registros = response.json()

conexao = sqlite3.connect("athlete_performance.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS wellness (
    data TEXT PRIMARY KEY,
    hrv REAL,
    resting_hr INTEGER,
    sleep_seconds INTEGER,
    sleep_score REAL,
    weight REAL,
    ctl REAL,
    atl REAL
)
""")

for registro in registros:
    cursor.execute("""
    INSERT OR REPLACE INTO wellness
    (data, hrv, resting_hr, sleep_seconds,
     sleep_score, weight, ctl, atl)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        registro.get("id"),
        registro.get("hrv"),
        registro.get("restingHR"),
        registro.get("sleepSecs"),
        registro.get("sleepScore"),
        registro.get("weight"),
        registro.get("ctl"),
        registro.get("atl")
    ))

conexao.commit()

cursor.execute("SELECT COUNT(*) FROM wellness")
total = cursor.fetchone()[0]

print(f"Registros salvos no banco: {total}")
print("Banco criado: athlete_performance.db")

conexao.close()
