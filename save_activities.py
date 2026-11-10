
import os
import json
import sqlite3
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

API_KEY = os.getenv("INTERVALS_API_KEY")
BASE_URL = "https://intervals.icu/api/v1"

response = requests.get(
    f"{BASE_URL}/athlete/0/activities",
    auth=HTTPBasicAuth("API_KEY", API_KEY),
    params={
        "oldest": "2026-10-01",
        "newest": "2026-11-09"
    },
    timeout=30
)

response.raise_for_status()
atividades = response.json()

conexao = sqlite3.connect("athlete_performance.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS activities (
    id TEXT PRIMARY KEY,
    data TEXT,
    nome TEXT,
    esporte TEXT,
    duracao INTEGER,
    distancia REAL,
    dados_json TEXT
)
""")

for atividade in atividades:
    cursor.execute("""
    INSERT OR REPLACE INTO activities
    (id, data, nome, esporte, duracao, distancia, dados_json)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        atividade.get("id"),
        atividade.get("start_date_local"),
        atividade.get("name"),
        atividade.get("type"),
        atividade.get("moving_time"),
        atividade.get("distance"),
        json.dumps(atividade)
    ))

conexao.commit()

cursor.execute("""
SELECT esporte, COUNT(*)
FROM activities
GROUP BY esporte
""")

print("ATIVIDADES SALVAS:")
for esporte, quantidade in cursor.fetchall():
    print(f"{esporte}: {quantidade}")

conexao.close()
