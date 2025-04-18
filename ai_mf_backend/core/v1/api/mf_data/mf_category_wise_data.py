from typing import Optional, List

from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.v1.api import limiter

from fastapi import APIRouter, Query
from asgiref.sync import sync_to_async


from ai_mf_backend.models.v1.api.mf_category_wise import MFCategoryOptionResponse, MFSubCategoryOptionResponse
from ai_mf_backend.models.v1.database.mf_category_wise import MutualFundType
from ai_mf_backend.models.v1.database.mf_master_data import MFSchemeIsInMaster


router = APIRouter()

@router.get("/mf_options_fund_category", response_model=MFCategoryOptionResponse)
async def get_mf_category_options():
    try:
        categories = await sync_to_async(list)(MutualFundType.objects.all())

        category_options = [
            {
                "key": int(category.id),
                "label": category.fund_type,
                "value": category.fund_type.lower(),
            }
            for category in categories
        ]

        data = {
            "blog_categories": {
                "name": "mf_category",
                "label": "MF Category",
                "options": category_options,
                "type": "dropdown",
                "default": [category_options[0]["key"]] if category_options else [],
                "required": False,
            }
        }

        return MFCategoryOptionResponse(
            status=True,
            message="Mutual Fund category options fetched successfully",
            data=data,
            status_code=200,
        )

    except Exception as e:
        return MFCategoryOptionResponse(
            status=False,
            message=f"Failed to fetch mutual fund category options: {str(e)}",
            data={},
            status_code=500,
        )

@router.get("/mf_options_fund_subcategory/",
            response_model = MFSubCategoryOptionResponse)
async def get_mf_subcategory_options(
    category_id: int = Query(..., ge=1, title="ID of the Fund Category")
):
    try:
        category_name = await sync_to_async(
            MutualFundType.objects.get
        )(deleted=False, fund_type=category_id)

        category_name = category_name.fund_type

        subcategories = await sync_to_async(list)(
            MFSchemeIsInMaster.objects.filter(asset_type=category_name)
        )

        return MFSubCategoryOptionResponse(
            status=False,
            message="Successfully fetched mutual fund category options",
            data=subcategories,
            status_code=500,
        )
        
    except Exception as e:
        return MFSubCategoryOptionResponse(
            status=False,
            message=f"Failed to fetch mutual fund category options: {str(e)}",
            data={},
            status_code=500,
        )



# @limiter.limit(api_config.REQUEST_PER_MIN)
# @router.get(
#     "/get_fund_data_category_subcategory_wise",
#     response_model=MFDataCategorySubcategoryWise,
# )
# async def filter_and_select_blog_data(
#     request: Request,
#     fund_category: Optional[str] = Query(
#         default=None,
#     ),
#     fund_subcategory: Optional[List[int]] = Query(
#         default=None, 
#     ),
# ):
#     allowed_params = ["fund_category", "fund_subcategory"]
#     try:
#         validate_query_params(dict(request.query_params), allowed_params)
#     except ValueError as e:
#         response.status_code = 400
#         return BlogCardResponse(
#             status=False,
#             message=str(e),
#             data=[],
#             status_code=response.status_code,
#         )
    
    