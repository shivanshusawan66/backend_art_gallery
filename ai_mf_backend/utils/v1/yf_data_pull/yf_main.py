import requests

import logging

from datetime import datetime
from lxml import html
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import time
from django.db import transaction
from django.core.management.base import BaseCommand
from decimal import Decimal, InvalidOperation
from ai_mf_backend.models.v1.database.mutual_fund import (
    AnnualReturn,
    FundData,
    HistoricalData,
    MutualFund,
    PerformanceData,
    RiskStatistics,
    TrailingReturn,
    FundOverview,
)
from ai_mf_backend.utils.v1.yf_data_pull.fetch_and_extract_data import fetch_and_extract_data
from ai_mf_backend.utils.v1.yf_data_pull.fetch_historical_data import fetch_historical_data
from ai_mf_backend.utils.v1.yf_data_pull.fetch_symbol import fetch_symbol
from ai_mf_backend.utils.v1.yf_data_pull.scrape_fund_data import scrape_fund_data
from ai_mf_backend.utils.v1.yf_data_pull.scrape_fund_performance import scrape_fund_performance


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create a session with retry logic
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))
from decimal import Decimal
import re


def clean_value(value):
    # Remove whitespace and unwanted characters
    if not value:
        return None

    # Remove common currency symbols and commas
    cleaned_value = re.sub(r"[^\d.]+", "", value)

    # Check for empty cleaned value
    if cleaned_value == "":
        return None

    return cleaned_value


def clean_net_assets(value):
    cleaned_value = clean_value(value)  # Ensure this returns a valid numeric string

    # Example: Define a multiplier (if you have a specific multiplier, use that)
    multiplier = Decimal("1.0")  # Make sure this is a Decimal

    # Convert cleaned_value to Decimal and multiply
    return Decimal(cleaned_value) * multiplier if cleaned_value else None


def clean_percentage(value):
    """
    Convert a percentage string or number to a Decimal.

    Args:
        value (str or float): The percentage value as a string (e.g., "75%") or a float.

    Returns:
        Decimal: The converted percentage as a Decimal.
    """
    if isinstance(value, str):
        # Remove whitespace and check if it ends with '%'
        value = value.strip()
        if value.endswith("%"):
            value = value[:-1].strip()  # Remove the '%' sign

        try:
            # Convert to Decimal
            return Decimal(value) / 100  # Convert percentage string to Decimal
        except (InvalidOperation, ValueError) as e:
            logging.error(f"Invalid percentage string: '{value}'. Error: {e}")
            return Decimal(0)  # Return 0 for invalid input

    elif isinstance(value, (int, float)):
        # Handle numeric types directly
        return Decimal(value) / 100

    logging.error(f"Expected string or numeric but got {type(value).__name__}: {value}")
    return Decimal(0)  # Return 0 for unsupported types


def convert_inception_date(date_str):
    if date_str:
        try:
            # Convert the date from "Apr 19, 2002" to YYYY-MM-DD
            return datetime.strptime(date_str, "%b %d, %Y").date()
        except ValueError:
            print(f"Error parsing date: {date_str}")
            return None  # Handle invalid date formats
    return None  # Return None if the string is empty


class Command(BaseCommand):
    help = "Fetch and populate mutual fund data"

    def handle(self, *args, **options):
        amfi_api_url = "https://www.amfiindia.com/spages/NAVOpen.txt?t=22112019"
        data_dict = fetch_and_extract_data(amfi_api_url, limit=20)

        count = 0
        for scheme_name, details in data_dict.items():
            symbol = fetch_symbol(details["q_param"])
            details["symbol"] = symbol

            if symbol != "N/A":
                with transaction.atomic():
                    # Create or update MutualFund
                    fund, created = MutualFund.objects.update_or_create(
                        scheme_name=scheme_name,
                        defaults={
                            "q_param": details["q_param"],
                            "net_asset_value": Decimal(details["net_asset_value"]),
                            "date": datetime.strptime(
                                details["date"], "%d-%b-%Y"
                            ).date(),
                            "symbol": symbol,
                        },
                    )

                    # Save historical data
                    historical_data = fetch_historical_data(symbol)
                    if historical_data:
                        for record in historical_data:
                            HistoricalData.objects.update_or_create(
                                fund=fund,
                                date=record["Date"],
                                defaults={
                                    "open": Decimal(str(record["Open"])),
                                    "high": Decimal(str(record["High"])),
                                    "low": Decimal(str(record["Low"])),
                                    "close": Decimal(str(record["Close"])),
                                    "adj_close": Decimal(str(record["Adj Close"])),
                                    "volume": int(record["Volume"]),
                                },
                            )

                    # Save performance data
                    performance_url = (
                        f"https://finance.yahoo.com/quote/{symbol}/performance/"
                    )
                    performance_data = scrape_fund_performance(performance_url)

                    if (
                        "Performance Overview" in performance_data
                        and performance_data["Performance Overview"]
                    ):
                        # Access the first section of 'Performance Overview'
                        overview_section = performance_data["Performance Overview"][0]

                        if "data" in overview_section and overview_section["data"]:
                            # Grab the data, which is a list
                            overview_list = overview_section["data"]

                            # Log the contents of the overview_list for debugging
                            logging.info(f"Overview list contents: {overview_list}")

                            # Initialize a dictionary to hold the extracted values
                            overview = {}

                            # Convert the overview_list to a dictionary for easier access
                            for item in overview_list:
                                if (
                                    len(item) == 2
                                ):  # Ensure it has both a key and a value
                                    key, value = item
                                    overview[key] = value

                            # Log the transformed overview dictionary for debugging
                            logging.info(f"Transformed overview dictionary: {overview}")

                            # Now proceed to update or create the PerformanceData object
                            perf, _ = PerformanceData.objects.update_or_create(
                                fund=fund,
                                defaults={
                                    "morningstar_return_rating": overview.get(
                                        "Morningstar Return Rating", ""
                                    ),
                                    "ytd_return": self.parse_percentage(
                                        overview.get("YTD Return", "0%")
                                    ),
                                    "average_return_5y": self.parse_percentage(
                                        overview.get("5y Average Return", "0%")
                                    ),
                                    "number_of_years_up": (
                                        int(overview.get("Number of Years Up", "0"))
                                        if overview.get("Number of Years Up")
                                        not in ["--", ""]
                                        else 0
                                    ),
                                    "number_of_years_down": (
                                        int(overview.get("Number of Years Down", "0"))
                                        if overview.get("Number of Years Down")
                                        not in ["--", ""]
                                        else 0
                                    ),
                                    "best_1y_total_return": self.parse_percentage(
                                        overview.get(
                                            "Best 1Y Total Return (Oct 1, 2024)", "0%"
                                        )
                                    ),
                                    "worst_1y_total_return": self.parse_percentage(
                                        overview.get(
                                            "Worst 1Y Total Return (Oct 1, 2024)", "0%"
                                        )
                                    ),
                                    "best_3y_total_return": self.parse_percentage(
                                        overview.get("Best 3Y Total Return", "0%")
                                    ),
                                    "worst_3y_total_return": self.parse_percentage(
                                        overview.get("Worst 3Y Total Return", "0%")
                                    ),
                                },
                            )
                        else:
                            logging.error(
                                "'data' section not found in the 'Performance Overview'."
                            )
                    else:
                        logging.error(
                            "'Performance Overview' section not found in the scraped data."
                        )
                    # Extract Fund Overview
                    # Assuming performance_data is already defined and populated
                    if (
                        "Fund Overview" in performance_data
                        and performance_data["Fund Overview"]
                    ):
                        fund_overview_section = performance_data["Fund Overview"][0]

                        if (
                            "data" in fund_overview_section
                            and fund_overview_section["data"]
                        ):
                            fund_overview_list = fund_overview_section["data"]

                            # Log the contents of the fund_overview_list for debugging
                            logging.info(
                                f"Fund Overview list contents: {fund_overview_list}"
                            )

                            # Initialize a dictionary to hold the extracted values for Fund Overview
                            fund_overview = {}

                            # Convert the fund_overview_list to a dictionary for easier access
                            for item in fund_overview_list:
                                if (
                                    len(item) == 2
                                ):  # Ensure it has both a key and a value
                                    key, value = item
                                    fund_overview[key] = value

                            # Log the transformed fund_overview dictionary for debugging
                            logging.info(
                                f"Transformed Fund Overview dictionary: {fund_overview}"
                            )

                            # Use the function to convert the inception date
                            inception_date = convert_inception_date(
                                fund_overview.get("Inception Date", "")
                            )

                            # Update or create the FundOverviewData object
                            fund_overview_data, _ = (
                                FundOverview.objects.update_or_create(
                                    fund=fund,
                                    defaults={
                                        "category": fund_overview.get("Category", ""),
                                        "fund_family": fund_overview.get(
                                            "Fund Family", ""
                                        ),
                                        "net_assets": clean_net_assets(
                                            fund_overview.get("Net Assets", "0")
                                        ),
                                        "ytd_return": clean_percentage(
                                            fund_overview.get("YTD Return", "0%")
                                        ),
                                        "yield_value": clean_percentage(
                                            fund_overview.get("Yield", "0%")
                                        ),
                                        "morningstar_rating": fund_overview.get(
                                            "Morningstar Rating", ""
                                        ),
                                        "inception_date": inception_date,  # Use the converted inception date
                                    },
                                )
                            )
                        else:
                            logging.error(
                                "'data' section not found in the 'Fund Overview'."
                            )
                    else:
                        logging.error(
                            "'Fund Overview' section not found in the scraped data."
                        )
                    if "Trailing Returns (%) Vs. Benchmarks" in performance_data:
                        trailing_returns = performance_data[
                            "Trailing Returns (%) Vs. Benchmarks"
                        ][0]["data"]
                        for tr in trailing_returns:
                            TrailingReturn.objects.update_or_create(
                                fund=fund,
                                metric=tr["Metric"],
                                defaults={
                                    "fund_return": self.parse_percentage(
                                        tr["Values"][0]
                                    ),
                                    "benchmark_return": self.parse_percentage(
                                        tr["Values"][1]
                                    ),
                                },
                            )

                    if "Annual Total Return (%) History" in performance_data:
                        annual_returns = performance_data[
                            "Annual Total Return (%) History"
                        ][0]["data"]
                        for ar in annual_returns:
                            AnnualReturn.objects.update_or_create(
                                fund=fund,
                                year=int(ar["Key"]),
                                defaults={
                                    "fund_return": self.parse_percentage(
                                        ar["Values"][1]
                                    ),
                                    "category_return": (
                                        self.parse_percentage(ar["Values"][2])
                                        if len(ar["Values"]) > 2
                                        else None
                                    ),
                                },
                            )

                    # Save fund data
                    fund_data = scrape_fund_data(symbol)
                    fund_details, _ = FundData.objects.update_or_create(
                        fund=fund,
                        defaults={
                            "min_initial_investment": Decimal(
                                fund_data.get("Min Initial Investment", "0").replace(
                                    ",", ""
                                )
                            ),
                            "min_subsequent_investment": Decimal(
                                fund_data.get("Min Subsequent Investment", "0").replace(
                                    ",", ""
                                )
                            ),
                        },
                    )

                    # Save risk statistics
                    risk_stats = fund_data.get("Risk Statistics", {})
                    for period, stats in risk_stats.items():
                        RiskStatistics.objects.update_or_create(
                            fund=fund,
                            period=period,
                            defaults={
                                "alpha": self.parse_percentage(stats.get("Alpha", "0")),
                                "beta": self.parse_percentage(stats.get("BETA", "0")),
                                "mean_annual_return": self.parse_percentage(
                                    stats.get("Mean Annual Return", "0")
                                ),
                                "r_squared": self.parse_percentage(
                                    stats.get("R-squared", "0")
                                ),
                                "standard_deviation": self.parse_percentage(
                                    stats.get("Standard Deviation", "0")
                                ),
                                "sharpe_ratio": self.parse_percentage(
                                    stats.get("Sharpe Ratio", "0")
                                ),
                                "treynor_ratio": self.parse_percentage(
                                    stats.get("Treynor Ratio", "0")
                                ),
                            },
                        )

                count += 1

            # Add a delay between processing each fund
            time.sleep(2)

        self.stdout.write(
            self.style.SUCCESS(f"Total number of funds processed: {count}")
        )

    def parse_percentage(self, value):
        try:
            return Decimal(value.rstrip("%"))
        except InvalidOperation:
            return Decimal("0")


if __name__ == "__main__":
    Command().handle()
