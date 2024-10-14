import requests
from bs4 import BeautifulSoup

import logging

from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import time


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create a session with retry logic
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))


def scrape_fund_data(symbol):
    base_url = f"https://finance.yahoo.com/quote/{symbol}"
    urls = {"purchase_info": f"{base_url}/purchase-info", "risk": f"{base_url}/risk"}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    fund_data = {}

    def extract_purchase_info(soup):
        items = soup.find_all("div", class_="item yf-1rkv3ys")
        for item in items:
            label = item.find("dt", class_="yf-1rkv3ys").text.strip()
            value = item.find("dd", class_="yf-1rkv3ys").text.strip()
            fund_data[label] = value

    def extract_risk_data(soup):
        risk_statistics = {"3_Years": {}, "5_Years": {}, "10_Years": {}}

        statistics_section = soup.find(
            "section", {"data-testid": "risk-statistics-table"}
        )
        if statistics_section:
            rows = statistics_section.find_all("tr")[1:]  # Skip the header row
            for row in rows:
                cols = row.find_all("td")
                if len(cols) > 0:
                    label = cols[0].text.strip()
                    risk_statistics["3_Years"][label] = cols[1].text.strip()
                    risk_statistics["5_Years"][label] = cols[3].text.strip()
                    risk_statistics["10_Years"][label] = cols[5].text.strip()

        fund_data["Risk Statistics"] = risk_statistics

        if not risk_statistics:
            logging.warning(
                "No risk statistics found. Please check the structure of the page."
            )

    for page, url in urls.items():
        try:
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            if page == "purchase_info":
                extract_purchase_info(soup)
            elif page == "risk":
                extract_risk_data(soup)
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch {page} data for symbol {symbol}: {str(e)}")

        # Add a delay between requests
        time.sleep(1)

    return fund_data
