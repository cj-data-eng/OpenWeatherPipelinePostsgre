
# Weather ETL Pipeline — Docker, Airflow & Snowflake

A scheduled ETL pipeline that pulls current weather data from the OpenWeatherMap API, transforms it, and loads it into Snowflake using an idempotent MERGE. Orchestrated with Apache Airflow, running in Docker on WSL2.

This is Phase 2 of a two-phase project. Phase 1 (Python + Postgres, run manually) lives on the `main` branch of this repo.

## Architecture

OpenWeatherMap API
|
[extract] -- Airflow Variable holds the API key
|
[transform] -- flattens JSON, adds explicit units, UTC timestamps
|
[load] -- stages rows, MERGEs into Snowflake (idempotent)
|
Snowflake (WEATHER_DB.RAW.WEATHER_READINGS)


Three tasks, one Airflow DAG (`weather_etl`), scheduled daily. A failure in any task triggers a push notification via ntfy.sh.

## Tech stack

- Apache Airflow 3.3.2 (CeleryExecutor), running in Docker on WSL2 (no Docker Desktop)
- Snowflake (XSMALL warehouse, 60s auto-suspend, monthly credit cap via a resource monitor)
- Python: `requests`, Airflow's Snowflake and Postgres providers
- Secrets managed via Airflow Variables and Connections, not `.env` files

## Project structure

.
├── docker-compose.yaml # official Airflow compose file, LOAD_EXAMPLES off
├── dags/
│ ├── weather_etl_dag.py # the DAG: extract -> transform -> load, TaskFlow API
│ └── weather_etl_lib/
│ ├── extract.py # API calls, reads API key from Airflow Variable
│ ├── transform.py # cleaning/flattening (unchanged from Phase 1)
│ ├── load.py # Postgres loader (kept for reference)
│ └── load_snowflake.py # Snowflake loader: stage table + MERGE
├── config/ # Airflow's own config dir + Snowflake private key (gitignored)
├── app_config/ # legacy Phase-1-style settings, unused on this branch


## Setup

1. Requires WSL2, Docker (CLI, not Desktop), and a Snowflake account with key-pair auth already set up.

2. Clone the repo and check out this branch:
```bash
   git clone https://github.com/cj-data-eng/OpenWeatherPipelinePostsgre.git
   cd OpenWeatherPipelinePostsgre
   git checkout airflow-snowflake
```

3. Create `.env` (not committed):

AIRFLOW_UID=1000
FERNET_KEY=<generate with cryptography.fernet.Fernet>
OPENWEATHER_API_KEY=<not actually used here, kept for reference>


4. Place your Snowflake private key at `config/snowflake_key_pkcs8.pem` (gitignored).

5. Start the stack:
```bash
   docker compose up airflow-init
   docker compose up -d
```

6. Set the Airflow Variable and Connections (see commands below).

7. In Snowflake, create the warehouse, database, schema, table, resource monitor, and a dedicated role scoped to only what the pipeline needs (see `sql/` in the repo history, or the Snowsight setup block used during development).

## Airflow Variable and Connections

```bash
docker compose run --rm airflow-cli airflow variables set openweather_api_key "<your key>"
```

```bash
docker compose run --rm airflow-cli airflow connections add 'weather_snowflake' --conn-type snowflake --conn-login 'YOUR_USER' --conn-schema 'RAW' --conn-extra '{"account": "YOUR_ORG-YOUR_ACCOUNT", "warehouse": "WEATHER_WH", "database": "WEATHER_DB", "role": "WEATHER_PIPELINE_ROLE", "private_key_file": "/opt/airflow/config/snowflake_key_pkcs8.pem"}'
```

## Running it

```bash
docker compose run --rm airflow-cli airflow dags unpause weather_etl
docker compose run --rm airflow-cli airflow dags trigger weather_etl
docker compose run --rm airflow-cli airflow dags list-runs weather_etl
```

Or just leave it running — it's scheduled `@daily`.

## What I learned

- Structuring a DAG with the TaskFlow API (`@task`), replacing manual XCom push/pull
- Storing secrets in Airflow Variables and Connections instead of `.env`, and why that matters once code runs inside containers
- Writing a Snowflake MERGE-based loader (stage table, then MERGE) as the idempotent equivalent of a Postgres `ON CONFLICT` upsert
- Debugging real infrastructure issues across the stack: Docker Engine vs Docker Desktop on WSL2, `host.docker.internal` not resolving to a Windows host as expected, a psycopg2/psycopg3 driver mismatch, an incorrect Snowflake account identifier format, and a Snowflake connection missing its schema
- Scoping a dedicated Snowflake role instead of running a pipeline as ACCOUNTADMIN
- Controlling Snowflake compute cost with warehouse auto-suspend and a resource monitor before ever turning on a schedule
- Adding failure alerting via a DAG-level `on_failure_callback`

## Relationship to Phase 1

The `extract.py` and `transform.py` logic is functionally the same as the `main` branch's Python + Postgres version. Only the load step and the orchestration changed — which was the point: proving the same pipeline logic can move from a manually-run script into a scheduled, containerized, cloud-warehouse pipeline without a rewrite.
