import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

API_KEY = os.getenv("INTERVALS_API_KEY")
BASE_URL = "https://intervals.icu/api/v1"

auth = HTTPBasicAuth("API_KEY", API_KEY)

# Busca as atividades recentes
response = requests.get(
    f"{BASE_URL}/athlete/0/activities",
    auth=auth,
    params={
        "oldest": "2026-11-01",
        "newest": "2026-11-09"
    },
    timeout=30
)

response.raise_for_status()
activities = response.json()

# Seleciona a atividade mais recente
activity = activities[0]
activity_id = activity["id"]

print("\nATIVIDADE:", activity.get("name"))
print("ID:", activity_id)

# Busca os detalhes completos
details_response = requests.get(
    f"{BASE_URL}/activity/{activity_id}",
    auth=auth,
    params={"intervals": "true"},
    timeout=30
)

details_response.raise_for_status()
details = details_response.json()

print("\n===== DADOS DISPONÍVEIS =====")

for key, value in details.items():
    if not isinstance(value, (dict, list)):
        print(f"{key}: {value}")

print("\n===== INTERVALOS =====")

intervals = details.get("icu_intervals", [])

for interval in intervals:
    print(interval)