# Weather ETL Pipeline

A simple ETL pipeline that pulls current weather data from the OpenWeatherMap API, cleans and flattens it, and loads it into PostgreSQL with idempotent upserts.

Built as Phase 1 of a two-phase project — this version runs locally with plain Python and Postgres. Phase 2 rebuilds the same pipeline logic to run on Docker + Airflow + Snowflake, scheduled rather than run manually.

## What it does

1. **Extract** — pulls current weather for a set of cities from the OpenWeatherMap API
2. **Transform** — flattens the nested JSON response into clean, typed rows with explicit units
3. **Load** — upserts rows into Postgres, deduped on `(city, observed_at)` so reruns don't create duplicates

## Tech stack

- Python 3
- `requests` for API calls
- `psycopg2` for Postgres
- `python-dotenv` for config

## Project structure

weather-etl-pipeline/
├── config/settings.py # reads .env, single source of config
├── sql/create_tables.sql # Postgres schema
├── src/
│ ├── extract.py # API calls
│ ├── transform.py # cleaning/flattening
│ ├── load.py # upsert into Postgres
│ └── pipeline.py # orchestrates extract -> transform -> load


## Setup

1. Clone the repo and create a virtual environment:
```bash
   python -m venv venv
   venv\Scripts\Activate.ps1   # Windows
   pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your own values:
```bash
   cp .env.example .env
```
   You'll need a free API key from [openweathermap.org](https://openweathermap.org/api).

3. Create the Postgres database and table:
```bash
   psql -U postgres -c "CREATE DATABASE weather_etl;"
   psql -U postgres -d weather_etl -f sql/create_tables.sql
```

4. Run the pipeline:
```bash
   python -m src.pipeline
```

## What I learned

- Structuring a Python project around ETL stages (extract/transform/load as separate files) rather than one script
- Writing idempotent upserts (`ON CONFLICT ... DO UPDATE`) to make pipeline reruns safe
- Managing secrets via `.env` instead of hardcoding credentials
- Debugging real infrastructure issues: PATH configuration, Windows service management, and a non-default Postgres port

## Next steps

Rebuilding this pipeline to run in Docker via Apache Airflow, loading into Snowflake instead of Postgres, on a scheduled interval instead of manual runs.