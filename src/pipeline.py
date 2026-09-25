import logging
from datetime import datetime

from src.extract import fetch_all_cities
from src.transform import transform_weather
from src.load import load_weather

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    logger.info("Pipeline started")

    logger.info("Extracting weather data...")
    raw_data = fetch_all_cities()
    logger.info(f"Extracted {len(raw_data)} raw records")

    logger.info("Transforming data...")
    clean_data = transform_weather(raw_data)
    logger.info(f"Transformed {len(clean_data)} records")

    logger.info("Loading data into Postgres...")
    load_weather(clean_data)

    logger.info("Pipeline finished successfully")


if __name__ == "__main__":
    run_pipeline()