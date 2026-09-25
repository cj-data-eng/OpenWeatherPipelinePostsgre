CREATE TABLE IF NOT EXISTS weather_readings (
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    temp_c NUMERIC(5, 2) NOT NULL,
    feels_like_c NUMERIC(5, 2) NOT NULL,
    humidity_pct INTEGER NOT NULL,
    pressure_hpa INTEGER NOT NULL,
    weather_main TEXT NOT NULL,
    weather_description TEXT NOT NULL,
    wind_speed_ms NUMERIC(5, 2) NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (city, observed_at)
);