import asyncio
import logging
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ai_mf_backend.models.v1.database.mf_master_data import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup (adjust your URL as needed)
DATABASE_URL = "postgresql://user:password@localhost:5432/yourdb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Example configuration for each data feed
# Each entry contains the API URL, the ORM model, and the primary key field for upsert.
data_feed_configs = [
    {
        "name": "AmcMaster",
        "url": "https://contentapi.accordwebservices.com/RawData/GetRawDataJSON?filename=Amc_mst_new&date=ddMMyyyy&section=MFMaster&sub=&token={token}",
        "model": MFAMCMaster,
        "primary_key": "amc_code",
    },
    # Add additional configurations for your other tables
]


async def fetch_data(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to fetch data from {url}, status: {response.status_code}")
        return None


def upsert_record(session, model, primary_key, record):
    """
    Upsert a single record where API attribute names match model attributes.
    """
    primary_value = record.get(primary_key)
    if primary_value is None:
        logger.warning(f"Primary key {primary_key} missing in record: {record}")
        return

    existing_record = (
        session.query(model)
        .filter(getattr(model, primary_key) == primary_value)
        .first()
    )

    if existing_record:
        # Update each attribute from the record
        for key, value in record.items():
            if hasattr(existing_record, key):
                setattr(existing_record, key, value)
    else:
        # Create a new record, filtering out any keys not present in the model (if necessary)
        new_record = model(**record)
        session.add(new_record)


def update_data_for_feed(config):
    """Fetch data from the endpoint and upsert records using the provided configuration."""
    session = SessionLocal()
    try:
        data = asyncio.run(fetch_data(config["url"]))
        if data is None:
            return
        for record in data:
            upsert_record(session, config["model"], config["primary_key"], record)
        session.commit()
        logger.info(f"Updated {config['name']} successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating {config['name']}: {e}")
    finally:
        session.close()


def update_all_feeds():
    """Loop over all configured feeds and update each table."""
    for config in data_feed_configs:
        update_data_for_feed(config)


# Example integration with APScheduler in FastAPI:
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()
scheduler = BackgroundScheduler()


@app.on_event("startup")
def startup_event():
    # Schedule the update_all_feeds to run at the desired interval (e.g., every 15 minutes)
    scheduler.add_job(update_all_feeds, "interval", minutes=15)
    scheduler.start()
    logger.info("Scheduler started")


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    logger.info("Scheduler shut down")


# Optional: Manual trigger endpoint
@app.get("/trigger_update")
async def trigger_update():
    # Run update_all_feeds asynchronously in a separate thread
    asyncio.create_task(asyncio.to_thread(update_all_feeds))
    return {"status": "Update triggered"}
