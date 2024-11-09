import requests
import logging
import yfinance as yf
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create a session with retry logic
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))


def fetch_historical_data(symbol: str) -> Optional[List[Dict[str, Any]]]:
    logging.info(f"Fetching historical data for symbol: {symbol}")
    try:
        historical_data = yf.download(symbol, period="max")
        historical_data.reset_index(inplace=True)
        return historical_data.to_dict(orient="records")
    except Exception as e:
        logging.error(f"Error fetching historical data for {symbol}: {e}")
        return None
