from fastapi import APIRouter, FastAPI
import requests
import csv
from io import StringIO
from django.db import transaction
from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.database.mutual_fund import AMFIMutualFund



router = APIRouter()
def fetch_and_extract_data(api_url):
    response = requests.get(api_url)
    
    if response.status_code != 200:
        print("Error: Failed to retrieve data.")
        return {}
    
    try:
        data = StringIO(response.text)
        reader = csv.DictReader(data, delimiter=';')
        
        results = {}
        
        for row in reader:
            scheme_name = row.get('Scheme Name')
            q_param = row.get('ISIN Div Payout/ ISIN Growth')
            if q_param and q_param.strip() and q_param.strip() != '-' and scheme_name:
                results[scheme_name] = q_param
        
        return results
    except Exception as e:
        print(f"Error parsing data: {e}")
        return {}
@sync_to_async
def update_or_create_mutual_funds(data_dict):
    with transaction.atomic():
        for scheme_name, q_param in data_dict.items():
            AMFIMutualFund.objects.update_or_create(
                scheme_name=scheme_name,
                defaults={'q_param': q_param}
            )
    return len(data_dict)
@sync_to_async
def get_all_mutual_funds():
    return list(AMFIMutualFund.objects.all().values('scheme_name', 'q_param'))
@router.post("/populate-data/")
async def populate_data():
    api_url = 'https://www.amfiindia.com/spages/NAVOpen.txt?t=22112019'
    data_dict = await sync_to_async(fetch_and_extract_data)(api_url)
    
    try:
        count = await update_or_create_mutual_funds(data_dict)
        return {"message": "Data populated successfully", "count": count}
    except Exception as e:
        return {"error": str(e)}
@router.get("/mutual-funds/")
async def get_mutual_funds():
    try:
        funds = await get_all_mutual_funds()
        return funds
    except Exception as e:
        return {"error": str(e)}    