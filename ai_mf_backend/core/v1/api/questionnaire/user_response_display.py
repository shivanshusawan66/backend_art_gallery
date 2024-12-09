from typing import Optional

from fastapi import APIRouter, Response, Depends, Query, Request
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
    UserResponseSchema,
)
from ai_mf_backend.config.v1.api_config import api_config

router = APIRouter()


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/get_user_questionnaire_response",
    response_model=UserQuestionnaireResponse,
    dependencies=[Depends(login_checker)],
)
async def get_user_questionnaire_responses(
    request: Request,
    response: Response,
    user_id: Optional[int] = Query(None, description="User ID"),
    section_id: Optional[int] = Query(None, description="Section ID"),
):
    try:
        if not user_id:
            response.status_code = 404
            return UserQuestionnaireResponse(
                status=False,
                message="User_id is not provided, please provide it",
                data={},
                status_code=404,
            )

        if not section_id:
            response.status_code = 404
            return UserQuestionnaireResponse(
                status=False,
                message="Section ID is not provided, please provide it",
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

        user_responses = await sync_to_async(list)(
            UserResponse.objects.filter(
                user_id=user_id, section_id=section_id, is_deleted=True
            )
        )
        if not user_responses:
            response.status_code = 404
            return UserQuestionnaireResponse(
                status=False,
                message="No user responses found.",
                data={},
                status_code=404,
            )

        user_responses = (
            [model_to_dict(response) for response in user_responses]
            if user_responses
            else []
        )

        user_responses = [
            UserResponseSchema.model_validate(response) for response in user_responses
        ]

        user_responses = [response.model_dump() for response in user_responses]

        return UserQuestionnaireResponse(
            status=True,
            message="Fetched user responses successfully.",
            data={"user_id": user_id, "responses": user_responses},
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
