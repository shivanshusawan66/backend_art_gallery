import logging

from asgiref.sync import sync_to_async

from fastapi import APIRouter, status, Response, Depends

from django.core.exceptions import ValidationError

from ai_mf_backend.core.v1.api import limiter

from ai_mf_backend.utils.v1.authentication.secrets import login_checker

from ai_mf_backend.models.v1.database.user import UserContactInfo
from ai_mf_backend.models.v1.api.questionnaire_responses import (
    SubmitQuestionnaireRequest,
    SubmitQuestionnaireResponse,
)
from ai_mf_backend.models.v1.database.questions import (
    Question,
    Section,
    Allowed_Response,
    UserResponse,
)

from ai_mf_backend.config.v1.api_config import api_config

router = APIRouter()

logger = logging.getLogger(__name__)


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.post(
    "/submit-questionnaire-response",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(login_checker)],
    response_model=SubmitQuestionnaireResponse,
)
async def submit_questionnaire_response(
    request: SubmitQuestionnaireRequest, response: Response
):
    try:
        # Fetch user
        user = await sync_to_async(
            UserContactInfo.objects.filter(user_id=request.user_id).first
        )()
        if not user:
            response.status_code = status.HTTP_404_NOT_FOUND
            return SubmitQuestionnaireResponse(
                status=False,
                message=f"This user with user id {request.user_id} does not exist.",
                data={"user_id": request.user_id},
                status_code=404,
            )

        # Validate section
        section = await sync_to_async(
            Section.objects.filter(id=request.section_id).first
        )()
        if not section:
            response.status_code = status.HTTP_404_NOT_FOUND
            return SubmitQuestionnaireResponse(
                status=False,
                message=f"Section with ID {request.section_id} not found",
                data={"user_id": request.user_id},
                status_code=404,
            )

        # Validate each response before temporarily saving it
        for response_item in request.responses:
            question_id = response_item.question_id
            user_response = response_item.response

            # Validate question existence
            question = await sync_to_async(
                Question.objects.filter(
                    id=question_id, section_id=request.section_id
                ).first
            )()
            if not question:
                response.status_code = status.HTTP_404_NOT_FOUND
                return SubmitQuestionnaireResponse(
                    status=False,
                    message=f"Question ID {question_id} not found in section {request.section_id}",
                    data={
                        "user_id": request.user_id,
                        "question_id": question_id,
                        "section_id": request.section_id,
                    },
                    status_code=404,
                )

            # Validate allowed response
            allowed_response = await sync_to_async(
                Allowed_Response.objects.filter(
                    question_id=question_id, response=user_response
                ).first
            )()
            if not allowed_response:
                response.status_code = status.HTTP_404_NOT_FOUND
                return SubmitQuestionnaireResponse(
                    status=False,
                    message=f"Invalid response '{user_response}' for question {question_id}",
                    data={
                        "user_id": request.user_id,
                        "response": user_response,
                        "question_id": question_id,
                    },
                    status_code=404,
                )

            # Create UserResponse instance
            user_response_instance = UserResponse(
                user_id=request.user_id,
                question_id=question_id,
                response_id=allowed_response.id,
                section_id=request.section_id,
            )
            try:
                # Validate the response
                await sync_to_async(user_response_instance.full_clean)()
            except ValidationError as e:
                response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
                return SubmitQuestionnaireResponse(
                    status=False,
                    message=f"Invalid response '{user_response}' for question {question_id}",
                    data={"errors": e.message_dict},
                    status_code=422,
                )

            await sync_to_async(user_response_instance.save)()

        response.status_code = status.HTTP_200_OK
        return SubmitQuestionnaireResponse(
            status=True,
            message="Successfully able to save responses to the Database.",
            data={},
            status_code=200,
        )
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return SubmitQuestionnaireResponse(
            status=False,
            message=f"Processing failed: {e}",
            data={},
            status_code=500,
        )
