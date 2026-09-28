from datetime import datetime, timedelta
from airflow.sdk import dag, task

from weather_etl_lib.extract import fetch_all_cities
from weather_etl_lib.transform import transform_weather
from weather_etl_lib.load import load_weather


@dag(
    dag_id="weather_etl",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=2)},
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