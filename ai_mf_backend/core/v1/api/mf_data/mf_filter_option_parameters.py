from fastapi import Response

from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.v1.api import limiter

from fastapi import APIRouter, Request, Response
from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.api.mf_filter_parameters import MFFilterColorOptionResponse, MFFilterParameterOptionResponse
from ai_mf_backend.models.v1.database.mf_filter_parameters import MFFilterColors, MFFilterParameters



router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/mf_options_filter_parameters", response_model=MFFilterParameterOptionResponse)
async def get_mf_options_filter_parameters(
    request: Request,
    response: Response,
):
    try:
        mf_filter_parameters = await sync_to_async(list)(MFFilterParameters.objects.all())

        options = [
            {
                "key": int(option.id),
                "label": option.parameter_name,
                "value": option.parameter_name.lower(),
            }
            for option in mf_filter_parameters
        ]

        data = {
            "fund_categories": {
                "name": "mf_filter_paramters",
                "label": "MF Filter Parameters",
                "options": options,
                "type": "dropdown",
                "default": [options[0]["key"]] if options else [],
                "required": False,
            }
        }

        response.status_code = 200
        return MFFilterParameterOptionResponse(
            status=True,
            message="Mutual Fund Filter Parameter options fetched successfully",
            data=data,
            status_code=response.status_code,
        )

    except Exception as e:
        response.status_code = 400
        return MFFilterParameterOptionResponse(
            status=False,
            message=f"Failed to fetch mutual fund filter paramter options: {str(e)}",
            data={},
            status_code=response.status_code,
        )
    
@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get("/mf_options_color", response_model=MFFilterColorOptionResponse)
async def get_mf_options_color(
    request: Request,
    response: Response,
):
    try:
        mf_filter_colors = await sync_to_async(list)(MFFilterColors.objects.all())

        options = [
            {
                "key": int(option.id),
                "label": option.color_name,
                "value": option.color_name.lower(),
            }
            for option in mf_filter_colors
        ]

        data = {
            "fund_categories": {
                "name": "mf_filter_colors",
                "label": "MF Filter Colors",
                "options": options,
                "type": "dropdown",
                "default": [options[0]["key"]] if options else [],
                "required": False,
            }
        }

        response.status_code = 200
        return MFFilterColorOptionResponse(
            status=True,
            message="Mutual Fund Filter Color options fetched successfully",
            data=data,
            status_code=response.status_code,
        )

    except Exception as e:
        response.status_code = 400
        return MFFilterColorOptionResponse(
            status=False,
            message=f"Failed to fetch mutual fund filter color options: {str(e)}",
            data={},
            status_code=response.status_code,
        )   