from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

MERGE_SQL = """
    MERGE INTO weather_readings AS t
    USING weather_readings_stage AS s
    ON t.city = s.city AND t.observed_at = s.observed_at
    WHEN MATCHED THEN UPDATE SET
        temp_c = s.temp_c,
        feels_like_c = s.feels_like_c,
        humidity_pct = s.humidity_pct,
        pressure_hpa = s.pressure_hpa,
        weather_main = s.weather_main,
        weather_description = s.weather_description,
        wind_speed_ms = s.wind_speed_ms,
        fetched_at = s.fetched_at
    WHEN NOT MATCHED THEN INSERT (
        city, country, temp_c, feels_like_c, humidity_pct, pressure_hpa,
        weather_main, weather_description, wind_speed_ms, observed_at, fetched_at
    ) VALUES (
        s.city, s.country, s.temp_c, s.feels_like_c, s.humidity_pct, s.pressure_hpa,
        s.weather_main, s.weather_description, s.wind_speed_ms, s.observed_at, s.fetched_at
    )
"""

INSERT_STAGE_SQL = """
    INSERT INTO weather_readings_stage (
        city, country, temp_c, feels_like_c, humidity_pct, pressure_hpa,
        weather_main, weather_description, wind_speed_ms, observed_at, fetched_at
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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

    hook = SnowflakeHook(snowflake_conn_id="weather_snowflake")
    conn = hook.get_conn()
    try:
        cur = conn.cursor()
        cur.execute("CREATE OR REPLACE TEMPORARY TABLE weather_readings_stage LIKE weather_readings")
        cur.executemany(INSERT_STAGE_SQL, values)
        cur.execute(MERGE_SQL)
        print(f"MERGE result (inserted, updated): {cur.fetchone()}")
    finally:
        conn.close()