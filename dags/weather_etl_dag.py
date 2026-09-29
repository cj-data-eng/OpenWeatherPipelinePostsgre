from datetime import datetime, timedelta
from airflow.sdk import dag, task

from weather_etl_lib.extract import fetch_all_cities
from weather_etl_lib.transform import transform_weather
from weather_etl_lib.load_snowflake import load_weather

import requests as http_requests

def notify_failure(context):
    dag_id = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    run_id = context["run_id"]
    http_requests.post(
        "https://ntfy.sh/dr_umar-airflow-alerts-6942",
        data=f"{dag_id} failed on task {task_id} (run {run_id})".encode("utf-8"),
        headers={"Title": "Airflow pipeline failure", "Priority": "high"},
        timeout=10,
    )

@dag(
    dag_id="weather_etl",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=2)},
    on_failure_callback=notify_failure,
    tags=["weather"],
)
def weather_etl():
    @task
    def extract():
        return fetch_all_cities()

    @task
    def transform(raw):
        return transform_weather(raw)

    @task
    def load(clean):
        load_weather(clean)

    load(transform(extract()))


weather_etl()