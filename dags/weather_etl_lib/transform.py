from datetime import datetime, timezone


def transform_weather(raw_data: list[dict]) -> list[dict]:
    """Flatten raw OpenWeatherMap JSON into clean rows for loading."""
    transformed = []

    for entry in raw_data:
        row = {
            "city": entry["name"],
            "country": entry["sys"]["country"],
            "temp_c": entry["main"]["temp"],
            "feels_like_c": entry["main"]["feels_like"],
            "humidity_pct": entry["main"]["humidity"],
            "pressure_hpa": entry["main"]["pressure"],
            "weather_main": entry["weather"][0]["main"],
            "weather_description": entry["weather"][0]["description"],
            "wind_speed_ms": entry["wind"]["speed"],
            "observed_at": datetime.fromtimestamp(entry["dt"], tz=timezone.utc),
            "fetched_at": datetime.now(timezone.utc),
        }
        transformed.append(row)

    return transformed


if __name__ == "__main__":
    from src.extract import fetch_all_cities

    raw = fetch_all_cities()
    clean = transform_weather(raw)
    for row in clean:
        print(row)