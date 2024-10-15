import requests
from bs4 import BeautifulSoup
import logging
from lxml import html
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


def find_symbol_and_agent(
    dom,
    xpath='//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[1]/div/section/h1',
):
    h1_tag = dom.xpath(xpath)

    if h1_tag:
        h1_text = h1_tag[0].text

        if "(" in h1_text:
            try:
                fund_name, symbol = h1_text.rsplit("(", 1)
                symbol = symbol.strip(")")
                return fund_name.strip(), symbol
            except ValueError:
                return "Error: Unable to split fund name and symbol correctly.", None
        else:
            return (
                "The h1 text does not contain a '('. Unable to split fund name and symbol.",
                None,
            )
    else:
        return "No element found with the given XPath.", None


def scrape_fund_performance(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the URL: {e}")
        return {}

    soup = BeautifulSoup(response.content, "html.parser")
    dom = html.fromstring(response.content)

    fund_name, symbol = find_symbol_and_agent(dom)

    main_container = soup.find(id="nimbus-app")
    if not main_container:
        logging.error("Main container with id='nimbus-app' not found.")
        return {}

    target_section = main_container.find_all("section")
    if not target_section:
        logging.error("No nested 'section' tags found within 'nimbus-app'.")
        return {}

    tables_data = {}

    for section in target_section:
        header = section.find("header")
        if not header:
            continue

        h3 = header.find("h3")
        if not h3:
            continue

        section_title = h3.get_text(strip=True)

        section_tables = []

        # Extract tables
        tables = section.find_all("table")
        for table in tables:
            table_data = []
            headers_row = table.find("tr")
            headers = []
            if table.find("th"):
                headers = [th.get_text(strip=True) for th in headers_row.find_all("th")]
            for row in table.find_all("tr")[1:] if headers else table.find_all("tr"):
                cells = row.find_all(["td", "th"])
                cell_text = [cell.get_text(strip=True) for cell in cells]
                if headers and len(cell_text) == len(headers):
                    row_dict = {headers[i]: cell_text[i] for i in range(len(headers))}
                else:
                    row_dict = cell_text

                # Convert Morningstar rating to asterisks
                if isinstance(row_dict, list) and len(row_dict) >= 2:
                    if row_dict[0] in ["Morningstar Rating", "Morningstar Risk Rating"]:
                        star_count = row_dict[1].count("\u2605")
                        row_dict[1] = "*" * star_count
                elif isinstance(row_dict, dict):
                    for key in ["Morningstar Rating", "Morningstar Risk Rating"]:
                        if key in row_dict:
                            star_count = row_dict[key].count("\u2605")
                            row_dict[key] = "*" * star_count

                table_data.append(row_dict)
            if table_data:
                section_tables.append({"type": "table", "data": table_data})

        # Extract definition lists (dl elements)
        dls = section.find_all("dl")
        for dl in dls:
            dl_data = []
            items = dl.find_all("div")
            for item in items:
                dt = item.find("dt")
                dds = item.find_all("dd")
                if dt and dds:
                    metric = dt.get_text(strip=True)
                    values = [dd.get_text(strip=True) for dd in dds]
                    dl_data.append({"Metric": metric, "Values": values})
            if dl_data:
                section_tables.append({"type": "dl", "data": dl_data})

        # Extract custom data rows (div elements with class 'dataRow')
        data_rows = section.find_all("div", class_="dataRow")
        if data_rows:
            custom_data = []
            for data_row in data_rows:
                dt = data_row.find("dt")
                dds = data_row.find_all("dd")
                if dt and dds:
                    key = dt.get_text(strip=True)
                    values = [dd.get_text(strip=True) for dd in dds]
                    custom_data.append({"Key": key, "Values": values})
            if custom_data:
                section_tables.append({"type": "dataRow", "data": custom_data})

        if section_tables:
            tables_data[section_title] = section_tables

    return tables_data
