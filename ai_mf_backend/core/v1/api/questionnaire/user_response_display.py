from typing import Optional

from fastapi import APIRouter,Response,Depends,Query
from asgiref.sync import sync_to_async
from django.forms.models import model_to_dict

from ai_mf_backend.core.v1.api import limiter

from ai_mf_backend.utils.v1.authentication.secrets import login_checker
from ai_mf_backend.models.v1.database.user import (
    UserContactInfo,
)
from ai_mf_backend.models.v1.database.questions import (
    UserResponse,
)
from ai_mf_backend.models.v1.api.questionnaire_responses import (
    UserQuestionnaireResponse,
)
from ai_mf_backend.config.v1.api_config import api_config

router=APIRouter()

# @limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/get_user_questionnaire_response",
    response_model=UserQuestionnaireResponse,
    dependencies=[Depends(login_checker)],
)
async def get_user_personal_financial_details(
    response: Response,
    user_id: Optional[int] = Query(None, description="User ID"),                               
):
    try:
        # Fetch user contact info
        if not user_id:
            response.status_code = 404
            return UserQuestionnaireResponse(
                status=False,
                message="User_id is not provided,please provide it",
                data={},
                status_code=404,
            )

        user_check = await UserContactInfo.objects.filter(user_id=user_id).aexists()

        if not user_check:
            response.status_code = 404
            return UserQuestionnaireResponse(
                status=False,
                message="User is not registered with the platform yet.",
                data={},
                status_code=404,
            )

        # Fetch user responses
        print("step1")
        user_responses = await sync_to_async(
                UserResponse.objects.filter(
                    user_id=user_id
                )
            )()
        print(user_responses)

        if not user_responses:
            response.status_code = 404
            return UserQuestionnaireResponse(
                status=False,
                message="No user responses found.",
                data={},
                status_code=404,
            )

        # Organize responses by section and question
        # data = {}
        # for user_response in user_responses:
        #     # Check if section and question exist
        #     if not user_response.section_id or not user_response.question_id:
        #         continue

        #     section_name = user_response.section_id.name
        #     question_text = user_response.question_id.question
        #     response_text = user_response.response_id.response if user_response.response_id else None

        #     # Group responses by section
        #     if section_name not in data:
        #         data[section_name] = {}

        #     data[section_name][question_text] = response_text

        return UserQuestionnaireResponse(
            status=True,
            message="Fetched user responses successfully.",
            data={},
            status_code=200,
        )
    except Exception as e:
        # General exception handling for any other issues
        return UserQuestionnaireResponse(
            status=False,
            message=f"An unexpected error occurred: {str(e)}",
            data={},
            status_code=500,
        )