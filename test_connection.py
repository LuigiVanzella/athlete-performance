import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

API_KEY = os.getenv("INTERVALS_API_KEY")

URL = "https://intervals.icu/api/v1/athlete/0/activities"

if not API_KEY:
    raise ValueError("API Key não encontrada!")

response = requests.get(
    URL,
    auth=HTTPBasicAuth("API_KEY", API_KEY),
    params={
        "oldest": "2026-11-01",
        "newest": "2026-11-09"
    },
    timeout=30
)

print("Status:", response.status_code)

if response.status_code == 200:
    activities = response.json()

    print("Conexão realizada!")
    print("Atividades encontradas:", len(activities))

    for activity in activities:
        print(
            activity.get("start_date_local"),
            activity.get("type"),
            activity.get("name")
        )
else:
    print("Erro:", response.text)