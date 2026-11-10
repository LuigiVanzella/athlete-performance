
import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

API_KEY = os.getenv("INTERVALS_API_KEY")
BASE_URL = "https://intervals.icu/api/v1"

atividades = {
    "CICLISMO": "i207995181",
    "CORRIDA": "i207846302"
}

campos = [
    "type",
    "moving_time",
    "distance",
    "average_watts",
    "weighted_average_watts",
    "icu_weighted_avg_watts",
    "icu_ftp",
    "icu_training_load",
    "average_heartrate",
    "max_heartrate",
    "average_cadence",
    "total_elevation_gain",
    "icu_efficiency_factor",
    "icu_power_hr",
    "icu_hr_decoupling",
    "pace",
    "average_speed"
]

for modalidade, activity_id in atividades.items():

    response = requests.get(
        f"{BASE_URL}/activity/{activity_id}",
        auth=HTTPBasicAuth("API_KEY", API_KEY),
        timeout=30
    )

    response.raise_for_status()
    atividade = response.json()

    print(f"\n===== {modalidade} =====")

    for campo in campos:
        valor = atividade.get(campo)

        if valor is not None:
            print(f"{campo}: {valor}")
