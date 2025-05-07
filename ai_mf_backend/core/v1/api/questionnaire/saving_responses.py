import logging

from asgiref.sync import sync_to_async

from fastapi import APIRouter, Request, status, Response, Depends

from django.core.exceptions import ValidationError

from ai_mf_backend.core.v1.tasks.questionnaire_scoring import assign_user_weights_chain
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

logger = logging.getLogger(__name__)

router = APIRouter(tags=["questionnaire"])


@router.post(
    "/submit_questionnaire_response",
    dependencies=[Depends(login_checker)],
    response_model=SubmitQuestionnaireResponse,
)
@limiter.limit(api_config.REQUEST_PER_MIN)
async def submit_questionnaire_response(
    request: Request, body: SubmitQuestionnaireRequest, response: Response
):
    try:
        user_id = body.user_id
        section_id = body.section_id
        responses = body.responses

        if user_id is None:
            response_status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            response.status_code = response_status_code
            return SubmitQuestionnaireResponse(
                status=False,
                message="User ID is required",
                data={},
                status_code=response_status_code,
            )

        try:
            user_instance = await UserContactInfo.objects.aget(user_id=user_id)
            if user_instance.questionnaire_filled:
                response_status_code = status.HTTP_200_OK
                response.status_code = response_status_code
                response_message = "Response updated in Database successfully"

            else:
                response_status_code = status.HTTP_201_CREATED
                response.status_code = response_status_code
                response_message = "Response saved to Database successfully"
                user_instance.questionnaire_filled = True
                await sync_to_async(user_instance.save)()

        except UserContactInfo.DoesNotExist:
            response_status_code = status.HTTP_404_NOT_FOUND
            response.status_code = response_status_code
            return SubmitQuestionnaireResponse(
                status=False,
                message=f"This user with user id {user_id} does not exist.",
                data={"user_id": user_id},
                status_code=response_status_code,
            )

        try:
            section_instance = await Section.objects.aget(pk=section_id)
        except Section.DoesNotExist:
            response_status_code = status.HTTP_404_NOT_FOUND
            response.status_code = response_status_code
            return SubmitQuestionnaireResponse(
                status=False,
                message=f"Section with ID {section_id} not found",
                data={"user_id": user_id},
                status_code=response_status_code,
            )

        if not len(responses):
            response_status_code = status.HTTP_400_BAD_REQUEST
            response.status_code = response_status_code
            return SubmitQuestionnaireResponse(
                status=False,
                message="The responses array cannot be empty. Provide at least one question-response pair.",
                data={"user_id": body.user_id},
                status_code=response_status_code,
            )

        validated_user_responses = list()

        for user_response in responses:
            question_id = user_response.question_id
            response_id = user_response.response_id

            try:
                question_instance = await Question.objects.filter(
                    pk=question_id, section_id=section_id
                ).aget()
            except Question.DoesNotExist:
                response_status_code = status.HTTP_404_NOT_FOUND
                response.status_code = response_status_code
                return SubmitQuestionnaireResponse(
                    status=False,
                    message=f"Question with ID {question_id} not found",
                    data={"user_id": user_id},
                    status_code=response_status_code,
                )

            try:
                response_instance = await Allowed_Response.objects.filter(
                    pk=response_id, question_id=question_id
                ).aget()
            except Allowed_Response.DoesNotExist:
                response_status_code = status.HTTP_400_BAD_REQUEST
                response.status_code = response_status_code
                return SubmitQuestionnaireResponse(
                    status=False,
                    message=f"Response for Question with ID {question_id} is not valid",
                    data={"user_id": user_id},
                    status_code=response_status_code,
                )

            user_response_instance = await sync_to_async(
                UserResponse.objects.filter(
                    user_id=user_id,
                    question_id=question_id,
                    section_id=section_id,
                ).first
            )()

            if not user_response_instance:
                user_response_instance = UserResponse(
                    user_id=user_instance,
                    question_id=question_instance,
                    response_id=response_instance,
                    section_id=section_instance,
                )
            else:
                user_response_instance.response_id = response_instance

            try:

                await sync_to_async(user_response_instance.full_clean)()
            except ValidationError as e:
                response_status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
                response.status_code = response_status_code
                return SubmitQuestionnaireResponse(
                    status=False,
                    message=f"Invalid response validation for question {question_id}",
                    data={"errors": e.message_dict},
                    status_code=response_status_code,
                )

            validated_user_responses.append(user_response_instance)

        for user_response_instance in validated_user_responses:
            await sync_to_async(user_response_instance.save)()

        await assign_user_weights_chain(user_id)

        response.status_code = response_status_code

        return SubmitQuestionnaireResponse(
            status=True,
            message=response_message,
            data={
                "user_id": user_id,
                "section_id": section_id,
            },
            status_code=response_status_code,
        )

    except Exception as e:
        logger.error(
            f"Error processing questionnaire response: {str(e)}", exc_info=True
        )
        response_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response.status_code = response_status_code
        return SubmitQuestionnaireResponse(
            status=False,
            message=f"Processing failed: {str(e)}",
            data={},
            status_code=response_status_code,
        )
