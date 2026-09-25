import requests
from config.settings import OPENWEATHER_API_KEY, CITIES

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(city: str) -> dict:
    """Fetch current weather for one city. Returns raw JSON as a dict."""
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",  # Celsius instead of Kelvin
    }
    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()  # throws an exception on 4xx/5xx instead of failing silently
    return response.json()


def fetch_all_cities() -> list[dict]:
    """Fetch weather for every city in CITIES. Returns a list of raw JSON dicts."""
    results = []
    for city in CITIES:
        try:
            data = fetch_weather(city)
            results.append(data)
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch weather for {city}: {e}")
            # deliberately continue rather than crash the whole batch over one city
    return results


if __name__ == "__main__":
    # lets you run this file directly to sanity-check the API call works,
    # separate from the full pipeline
    weather_data = fetch_all_cities()
    for entry in weather_data:
        print(entry)