import psycopg2
from psycopg2.extras import execute_values
from config.settings import DB_CONFIG

INSERT_QUERY = """
    INSERT INTO weather_readings (
        city, country, temp_c, feels_like_c, humidity_pct,
        pressure_hpa, weather_main, weather_description,
        wind_speed_ms, observed_at, fetched_at
    )
    VALUES %s
    ON CONFLICT (city, observed_at)
    DO UPDATE SET
        temp_c = EXCLUDED.temp_c,
        feels_like_c = EXCLUDED.feels_like_c,
        humidity_pct = EXCLUDED.humidity_pct,
        pressure_hpa = EXCLUDED.pressure_hpa,
        weather_main = EXCLUDED.weather_main,
        weather_description = EXCLUDED.weather_description,
        wind_speed_ms = EXCLUDED.wind_speed_ms,
        fetched_at = EXCLUDED.fetched_at;
"""


def load_weather(rows: list[dict]) -> None:
    """Upsert clean weather rows into Postgres."""
    if not rows:
        print("No rows to load.")
        return

    values = [
        (
            r["city"], r["country"], r["temp_c"], r["feels_like_c"],
            r["humidity_pct"], r["pressure_hpa"], r["weather_main"],
            r["weather_description"], r["wind_speed_ms"],
            r["observed_at"], r["fetched_at"],
        )
        for r in rows
    ]

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            execute_values(cur, INSERT_QUERY, values)
        conn.commit()
        print(f"Loaded {len(values)} rows.")
    finally:
        conn.close()


if __name__ == "__main__":
    from src.extract import fetch_all_cities
    from src.transform import transform_weather

    raw = fetch_all_cities()
    clean = transform_weather(raw)
    load_weather(clean)