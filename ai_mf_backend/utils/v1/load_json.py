# utils/load_json.py

import json
from typing import List, Dict


def load_funds_data() -> List[Dict]:
    """
    Utility function to load funds data from a JSON file located in the Datafiles directory.
    Returns:
        List[Dict]: A list of dictionaries representing the funds data.
    """
    file_path = "ai_mf_backend/Datafiles/mutual_fund_category.json"
    with open(file_path, "r") as file:
        funds_data = json.load(file)
    return funds_data
