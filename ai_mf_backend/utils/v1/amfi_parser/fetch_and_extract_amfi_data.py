import requests
import csv
from io import StringIO
from typing import Dict, Optional


def fetch_and_extract_amfi_data(api_url: str) -> Dict[str, str]:
    response: requests.Response = requests.get(api_url)

    if response.status_code != 200:
        print("Error: Failed to retrieve data.")
        return {}

    try:
        data: StringIO = StringIO(response.text)
        reader: csv.DictReader = csv.DictReader(data, delimiter=";")

        results: Dict[str, str] = {}

        for row in reader:
            scheme_name: Optional[str] = row.get("Scheme Name")
            q_param: Optional[str] = row.get("ISIN Div Payout/ ISIN Growth")
            if q_param and q_param.strip() and q_param.strip() != "-" and scheme_name:
                results[scheme_name] = q_param

        return results
    except Exception as e:
        print(f"Error parsing data: {e}")
        return {}
