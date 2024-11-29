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

        user_id = request.user_id
        section_id = request.section_id
        responses = request.responses

        # Fetch user
        user = await sync_to_async(UserContactInfo.objects.filter(pk=user_id).first)()
        if not user:
            response_status_code = status.HTTP_404_NOT_FOUND
            response.status_code = response_status_code
            return SubmitQuestionnaireResponse(
                status=False,
                message=f"This user with user id {user_id} does not exist.",
                data={"user_id": user_id},
                status_code=response_status_code,
            )

        # Validate section
        section = await sync_to_async(Section.objects.filter(pk=section_id).first)()
        if not section:
            response_status_code= status.HTTP_404_NOT_FOUND
            response.status_code = response_status_code
            return SubmitQuestionnaireResponse(
                status=False,
                message=f"Section with ID {section_id} not found",
                data={"user_id": user_id},
                status_code=response_status_code,
            )

        # Process and save all responses from previous section
        for user_response in responses:
            question_id = user_response.question_id
            response_id = user_response.response_id

            # Validate question and allowed response
            question = await sync_to_async(
                Question.objects.filter(pk=question_id, section_id=section_id).first
            )()
            if not question:
                response_status_code= status.HTTP_404_NOT_FOUND
                response.status_code = response_status_code
                return SubmitQuestionnaireResponse(
                    status=False,
                    message=f"Question with ID {question_id} not found",
                    data={"user_id": user_id},
                    status_code=response_status_code,
                )

            allowed_response = await sync_to_async(
                Allowed_Response.objects.filter(
                    question_id=question_id, pk=response_id
                ).first
            )()
            if not allowed_response:
                response_status_code = status.HTTP_400_BAD_REQUEST
                response.status_code = response_status_code
                return SubmitQuestionnaireResponse(
                    status=False,
                    message=f"Response for Question with ID {question_id} is not valid",
                    data={"user_id": user_id},
                    status_code=response_status_code,
                )

            # Get existing response or create new one
            user_response_instance = await sync_to_async(
                UserResponse.objects.filter(
                    user_id=user_id,
                    question_id=question_id,
                    response_id=response_id,
                    section_id=section_id,
                ).first
            )()

            if not user_response_instance:
                user_response_instance = UserResponse(
                    user_id=user,
                    question_id=question,
                    response_id=allowed_response,
                    section_id=section,
                )
                new_document = True
                response_status_code = status.HTTP_201_CREATED
            else:
                user_response_instance.response_id = allowed_response
                new_document = False
                response_status_code = status.HTTP_200_OK

            try:
                # Validate the response
                await sync_to_async(user_response_instance.full_clean)()
                await sync_to_async(user_response_instance.save)()
            except ValidationError as e:
                response_status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
                response.status_code = response_status_code
                return SubmitQuestionnaireResponse(
                    status=False,
                    message=f"Invalid response validation for question {question_id}",
                    data={"errors": e.message_dict},
                    status_code=response_status_code,
                )

        response.status_code = response_status_code
        return SubmitQuestionnaireResponse(
            status=True,
            message=(
                "Response saved to Database successfully"
                if new_document
                else "Response updated in database successfully"
            ),
            data={
                "user_id": user_id,
                "question_id": question_id,
                "response": response_id,
                "section": section_id,
            },
            status_code=response_status_code,
        )

    except Exception as e:
        logger.error(
            f"Error processing questionnaire response: {str(e)}", exc_info=True
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return SubmitQuestionnaireResponse(
            status=False,
            message=f"Processing failed: {str(e)}",
            data={},
            status_code=500,
        )
