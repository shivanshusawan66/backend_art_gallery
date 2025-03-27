from fastapi import APIRouter
from django.db import transaction
from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.database.mutual_fund import AMFIMutualFund
from ai_mf_backend.utils.v1.amfi_parser.fetch_and_extract_amfi_data import (
    fetch_and_extract_amfi_data,
)


router = APIRouter()


# Synchronous function for database updates
@sync_to_async
def update_or_create_mutual_funds_bulk(data_dict):
    with transaction.atomic():
        mutual_funds = [
            AMFIMutualFund(scheme_name=scheme_name, q_param=q_param)
            for scheme_name, q_param in data_dict.items()
        ]
        # Bulk create or update for optimization
        AMFIMutualFund.objects.bulk_create(mutual_funds, ignore_conflicts=True)
    return len(data_dict)


# Synchronous function to fetch all mutual funds
@sync_to_async
def get_all_mutual_funds():
    return list(AMFIMutualFund.objects.all().values("scheme_name", "q_param"))


# Endpoint to populate data
@router.post("/parse_amfi_data/")
async def populate_data():
    api_url = "https://www.amfiindia.com/spages/NAVOpen.txt?t=22112019"

    # Call fetch_and_extract_amfi_data synchronously (remove await)
    data_dict = fetch_and_extract_amfi_data(api_url)

    try:
        count = await update_or_create_mutual_funds_bulk(data_dict)
        return {"message": "Data populated successfully", "count": count}
    except Exception as e:
        return {"error": str(e)}


# Endpoint to get all mutual funds
@router.get("/amfi_mf_list/")
async def get_mutual_funds():
    try:
        funds = await get_all_mutual_funds()
        return funds
    except Exception as e:
        return {"error": str(e)}
