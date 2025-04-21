from django.apps import apps
from ai_mf_backend.config.v1.api_config import api_config 
from ai_mf_backend.models.v1.database.mf_master_data import MFSchemeMasterInDetails
from ai_mf_backend.models.v1.database.mf_reference_table import MFReferenceTable
from fastapi import APIRouter, Query, Request, Response
from typing import Optional
from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.api.mf_portfolio_section import(
    MFOptionandDetailsResponse,
)
from django.db.models import OuterRef, Subquery, F
from ai_mf_backend.core.v1.api import limiter 

router = APIRouter()

@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/get_mf_options_and_details", 
    response_model=MFOptionandDetailsResponse,
)
async def get_mf_options_and_details(
    request: Request,
    response: Response,
    fund_name: Optional[str] = Query(default=None, description="Search mutual fund name"),
):
    try:
        marker_list = ["status", "s_name", "navrs","frequency", "sip"]

        refs = await sync_to_async(lambda: list(MFReferenceTable.objects.filter(marker_name__in=marker_list)))()

        marker_to_models = {
            ref.marker_name: apps.get_model(api_config.PROJECT_NAME,ref.table_name)
            for ref in refs
            if ref.marker_name in marker_list
        }

        active_schemecodes = await sync_to_async(
            lambda: set(marker_to_models['status'].objects.filter(
                status="Active"
            ).values_list("schemecode", flat=True))
        )()

        base_query = MFSchemeMasterInDetails.objects.filter(schemecode__in=active_schemecodes)
        
        if fund_name:
            base_query = base_query.filter(s_name__icontains=fund_name)

        if "navrs" in marker_to_models:
            base_query = base_query.annotate(navrs=Subquery(
                marker_to_models["navrs"].objects.filter(
                    schemecode=OuterRef("schemecode"),
                ).values("navrs")[:1]
            ))

        ordered_query = base_query.order_by(F("s_name").asc(nulls_last=True))
        result_query = ordered_query.values("schemecode", "s_name", "navrs")
        full_results = await sync_to_async(lambda: list(result_query))()
        

        if "frequency" in marker_to_models:
            frequency_model = marker_to_models["frequency"]
            sip_frequency_data = await sync_to_async(lambda: list(
                frequency_model.objects.filter(
                    schemecode__in=active_schemecodes
                ).values("schemecode", "frequency", "sip")
            ))()
            
            # Create a clean dictionary structure
            sip_frequency_map = {}
            for item in sip_frequency_data:
                schemecode = item["schemecode"]
                if schemecode not in sip_frequency_map:
                    sip_frequency_map[schemecode] = {}
                sip_frequency_map[schemecode][item["frequency"]] = item["sip"]
            
            # Add to results
            for item in full_results:
                item["SIP Availabilty with Frequency"] = sip_frequency_map.get(item["schemecode"], {})

        response.status_code=200
        return MFOptionandDetailsResponse(
            status=True,
            message="Mutual funds options and its details feteched successfully",
            data=full_results,
            status_code=response.status_code,
        )
    
    except Exception as e:
        response.status_code=400
        return MFOptionandDetailsResponse(
            status=False,
            message=f"Error occurred: {str(e)}",
            data=[],
            status_code=response.status_code,
        )