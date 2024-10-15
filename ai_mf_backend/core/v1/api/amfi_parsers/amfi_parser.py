from fastapi import APIRouter
from django.db import transaction
from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.database.mutual_fund import AMFIMutualFund
from ai_mf_backend.utils.v1.yf_data_pull import fetch_and_extract_data



router = APIRouter()
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
@router.post("/parse-amfi-data/")
async def populate_data():
    api_url = 'https://www.amfiindia.com/spages/NAVOpen.txt?t=22112019'
    data_dict = await sync_to_async(fetch_and_extract_data)(api_url)
    
    try:
        count = await update_or_create_mutual_funds(data_dict)
        return {"message": "Data populated successfully", "count": count}
    except Exception as e:
        return {"error": str(e)}
@router.get("/amfi-mf-list/")
async def get_mutual_funds():
    try:
        funds = await get_all_mutual_funds()
        return funds
    except Exception as e:
        return {"error": str(e)}    