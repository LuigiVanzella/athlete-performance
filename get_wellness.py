
import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

API_KEY = os.getenv("INTERVALS_API_KEY")
BASE_URL = "https://intervals.icu/api/v1"
auth = HTTPBasicAuth("API_KEY", API_KEY)

response = requests.get(
    f"{BASE_URL}/athlete/0/wellness",
    auth=auth,
    params={
        "oldest": "2026-10-01",
        "newest": "2026-11-09"
    },
    timeout=30
)

response.raise_for_status()
wellness = response.json()

print("REGISTROS DE WELLNESS:", len(wellness))

print("HISTÓRICO DE WELLNESS:\n")

campos = [
    "id",
    "hrv",
    "restingHR",
    "sleepSecs",
    "sleepScore",
    "weight",
    "fatigue",
    "soreness",
    "stress",
    "readiness"
]

for registro in wellness:
    dados = {
        campo: registro.get(campo)
        for campo in campos
    }

    print(dados)
