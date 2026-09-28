import requests
from airflow.sdk import Variable

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
CITIES = ["London", "New York", "Tokyo", "Sydney"]


def fetch_weather(city: str) -> dict:
    api_key = Variable.get("openweather_api_key")
    params = {"q": city, "appid": api_key, "units": "metric"}
    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_all_cities() -> list[dict]:
    results = []
    for city in CITIES:
        try:
            results.append(fetch_weather(city))
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch weather for {city}: {e}")
    return results