import requests

import csv
from io import StringIO
import logging

from requests.adapters import HTTPAdapter
from urllib3.util import Retry


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create a session with retry logic
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))


def fetch_and_extract_data(api_url, limit=20):
    logging.info(f"Fetching data from {api_url}")
    response = requests.get(api_url)

    if response.status_code != 200:
        logging.error("Failed to retrieve data.")
        return {}

    try:
        data = StringIO(response.text)
        reader = csv.DictReader(data, delimiter=";")

        results = {}
        count = 0

        for row in reader:
            if count >= limit:
                break

            scheme_name = row.get("Scheme Name")
            q_param = row.get("ISIN Div Payout/ ISIN Growth")
            net_asset_value = row.get("Net Asset Value")
            date = row.get("Date")

            if q_param and q_param.strip() and q_param.strip() != "-" and scheme_name:
                results[scheme_name] = {
                    "q_param": q_param,
                    "net_asset_value": net_asset_value,
                    "date": date,
                }
                count += 1

        logging.info(f"Data extracted successfully for {count} funds.")
        return results
    except Exception as e:
        logging.error(f"Error parsing data: {e}")
        return {}
