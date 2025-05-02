from typing import Optional

from fastapi import APIRouter, Response, Depends, Query, Request, Header
from asgiref.sync import sync_to_async
from django.forms.models import model_to_dict

from ai_mf_backend.core.v1.api import limiter

from ai_mf_backend.utils.v1.authentication.secrets import (
    login_checker,
    jwt_token_checker,
)
from ai_mf_backend.models.v1.database.user import (
    UserContactInfo,
)
from ai_mf_backend.models.v1.database.questions import (
    UserResponse,
    Section,
)
from ai_mf_backend.models.v1.api.questionnaire_responses import (
    UserQuestionnaireResponse,
    UserResponseSchema,
)
from ai_mf_backend.config.v1.api_config import api_config

router = APIRouter()


@router.get(
    "/get_user_questionnaire_response",
    response_model=UserQuestionnaireResponse,
    dependencies=[Depends(login_checker)],
)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def get_user_questionnaire_responses(
    request: Request,
    response: Response,
    user_id: Optional[int] = Query(None, description="User ID"),
    section_id: Optional[int] = Query(None, description="Section ID"),
    Authorization: str = Header(),
):

    try:
        decoded_payload = jwt_token_checker(jwt_token=Authorization, encode=False)
        email = decoded_payload.get("email")
        mobile_no = decoded_payload.get("mobile_number")

        if not any([email, mobile_no]):
            response.status_code = 422
            return UserQuestionnaireResponse(
                status=False,
                message="Invalid JWT token: no email or mobile number found.",
                data={},
                status_code=response.status_code,
            )

        user = None
        if email:
            user = await UserContactInfo.objects.filter(email=email).afirst()
        elif mobile_no:
            user = await UserContactInfo.objects.filter(
                mobile_number=mobile_no
            ).afirst()

        if not user:
            response.status_code = 400
            return UserQuestionnaireResponse(
                status=False,
                message="User not found",
                data={},
                status_code=response.status_code,
            )
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
        section_valid = await Section.objects.filter(id=section_id).aexists()
        if not section_valid:
            response.status_code = 400
            return UserQuestionnaireResponse(
                status=False,
                message="Invalid ID provided for section_id.",
                data={},
                status_code=400,
            )
        user_check = await UserContactInfo.objects.filter(user_id=user_id).afirst()

        if not user_check:
            response.status_code = 404
            return UserQuestionnaireResponse(
                status=False,
                message="User is not registered with the platform yet.",
                data={},
                status_code=404,
            )
        if user_check.user_id != user.user_id:
            response.status_code = 403
            return UserQuestionnaireResponse(
                status=False,
                message="Unauthorized access. User ID does not match the token.",
                data={},
                status_code=403,
            )

        user_responses = await sync_to_async(list)(
            UserResponse.objects.filter(
                user_id=user_id, section_id=section_id, deleted=False
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
        return UserQuestionnaireResponse(
            status=False,
            message=f"An unexpected error occurred: {str(e)}",
            data={},
            status_code=500,
        )
