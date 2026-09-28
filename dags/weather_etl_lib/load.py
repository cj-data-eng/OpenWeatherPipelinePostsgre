from airflow.providers.postgres.hooks.postgres import PostgresHook

INSERT_QUERY = """
    INSERT INTO weather_readings (
        city, country, temp_c, feels_like_c, humidity_pct,
        pressure_hpa, weather_main, weather_description,
        wind_speed_ms, observed_at, fetched_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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

    hook = PostgresHook(postgres_conn_id="weather_postgres")
    conn = hook.get_conn()
    try:
        with conn.cursor() as cur:
            cur.executemany(INSERT_QUERY, values)
        conn.commit()
        print(f"Loaded {len(values)} rows.")
    finally:
        conn.close()