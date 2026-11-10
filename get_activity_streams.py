
import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

API_KEY = os.getenv("INTERVALS_API_KEY")
BASE_URL = "https://intervals.icu/api/v1"
auth = HTTPBasicAuth("API_KEY", API_KEY)

activity_id = "i207995181"

response = requests.get(
    f"{BASE_URL}/activity/{activity_id}/streams.json",
    auth=auth,
    params={
        "types": "watts,heartrate,cadence,velocity_smooth,altitude",
        "interval": "1"
    },
    timeout=30
)

response.raise_for_status()
streams = response.json()

print("TIPOS DE DADOS ENCONTRADOS:")
for stream in streams:
    print(
        stream.get("type"),
        "| quantidade:", len(stream.get("data", [])),
        "| amostra:", stream.get("data", [])[:10]
    )
