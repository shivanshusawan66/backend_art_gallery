import requests
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

def fetch_symbol(q_param: str) -> str:
    """Fetches the stock symbol for a given query parameter.

    Args:
        q_param (str): The query parameter for which to fetch the symbol.

    Returns:
        str: The stock symbol if found, otherwise "N/A".
    """
    logging.info(f"Fetching symbol for q_param: {q_param}")
    url = "https://query1.finance.yahoo.com/v1/finance/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    }

    params = {
        "q": q_param,
        "lang": "en-US",
        "region": "US",
        "quotesCount": "1",
        "newsCount": "0",
        "listsCount": "0",
    }

    response = session.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        quotes = data.get("quotes", [])
        if quotes:
            symbol = quotes[0].get("symbol")
            logging.info(f"Found symbol: {symbol} for q_param: {q_param}")
            return symbol
    else:
        logging.error(
            f"Request failed for q_param {q_param} with status code {response.status_code}"
        )

    return "N/A"
import requests
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

def fetch_symbol(q_param: str) -> str:
    """Fetches the stock symbol for a given query parameter.

    Args:
        q_param (str): The query parameter for which to fetch the symbol.

    Returns:
        str: The stock symbol if found, otherwise "N/A".
    """
    logging.info(f"Fetching symbol for q_param: {q_param}")
    url = "https://query1.finance.yahoo.com/v1/finance/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    }

    params = {
        "q": q_param,
        "lang": "en-US",
        "region": "US",
        "quotesCount": "1",
        "newsCount": "0",
        "listsCount": "0",
    }

    response = session.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        quotes = data.get("quotes", [])
        if quotes:
            symbol = quotes[0].get("symbol")
            logging.info(f"Found symbol: {symbol} for q_param: {q_param}")
            return symbol
    else:
        logging.error(
            f"Request failed for q_param {q_param} with status code {response.status_code}"
        )

    return "N/A"
