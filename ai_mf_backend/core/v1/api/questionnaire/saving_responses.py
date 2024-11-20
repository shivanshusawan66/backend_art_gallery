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
from typing import List, Dict

router = APIRouter()
logger = logging.getLogger(__name__)

# This will store the responses for each user and section temporarily
user_responses_storage: Dict[int, Dict[int, List[Dict]]] = {}

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
        user = await sync_to_async(UserContactInfo.objects.filter(pk=request.user_id).first)()
        if not user:
            response.status_code = status.HTTP_404_NOT_FOUND
            return SubmitQuestionnaireResponse(
                status=False,
                message=f"This user with user id {request.user_id} does not exist.",
                data={"user_id": request.user_id},
                status_code=404,
            )

        # Validate section
        section = await sync_to_async(Section.objects.filter(pk=request.section_id).first)()
        if not section:
            response.status_code = status.HTTP_404_NOT_FOUND
            return SubmitQuestionnaireResponse(
                status=False,
                message=f"Section with ID {request.section_id} not found",
                data={"user_id": request.user_id},
                status_code=404,
            )

        # Initialize storage for this user if not exists
        if request.user_id not in user_responses_storage:
            user_responses_storage[request.user_id] = {}

        # Check if user is changing sections
        previous_sections = list(user_responses_storage[request.user_id].keys())
        is_changing_section = previous_sections and request.section_id not in previous_sections

        # If changing section, save all responses from the previous section
        if is_changing_section:
            previous_section_id = previous_sections[-1]
            previous_responses = user_responses_storage[request.user_id].pop(previous_section_id, [])
            
            # Process and save all responses from previous section
            user_responses_to_save = []
            for prev_response in previous_responses:
                question_id = prev_response["question_id"]
                user_response_value = prev_response["response"]

                # Validate question and allowed response
                question = await sync_to_async(
                    Question.objects.filter(pk=question_id, section_id=previous_section_id).first
                )()

                allowed_response = await sync_to_async(
                    Allowed_Response.objects.filter(question_id=question_id, response=user_response_value).first
                )()

                prev_section = await sync_to_async(Section.objects.get)(pk=previous_section_id)
                
                # Get existing response or create new one
                user_response_instance = await sync_to_async(
                    UserResponse.objects.filter(
                        user_id=user,
                        question_id=question,
                        response_id=allowed_response,
                        section_id=prev_section
                    ).first
                )()

                if not user_response_instance:
                    user_response_instance = UserResponse(
                        user_id=user,
                        question_id=question,
                        response_id=allowed_response,
                        section_id=prev_section,
                    )
                else:
                    user_response_instance.response_id = allowed_response

                try:
                    # Validate the response
                    await sync_to_async(user_response_instance.full_clean)()
                    user_responses_to_save.append(user_response_instance)
                except ValidationError as e:
                    response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
                    return SubmitQuestionnaireResponse(
                        status=False,
                        message=f"Invalid response validation for question {question_id}",
                        data={"errors": e.message_dict},
                        status_code=422,
                    )

            # Batch save all validated responses
            for user_response_instance in user_responses_to_save:
                await sync_to_async(user_response_instance.save)()

        # Initialize storage for current section
        if request.section_id not in user_responses_storage[request.user_id]:
            user_responses_storage[request.user_id][request.section_id] = []

        # Validate and store current section's responses temporarily
        for response_item in request.responses:
            question_id = response_item.question_id
            user_response = response_item.response

            # Validate question
            question = await sync_to_async(
                Question.objects.filter(pk=question_id, section_id=request.section_id).first
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
                Allowed_Response.objects.filter(question_id=question_id, response=user_response).first
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

            # Store the validated response
            user_responses_storage[request.user_id][request.section_id].append({
                "question_id": question_id,
                "response": user_response,
            })

        response.status_code = status.HTTP_201_CREATED if is_changing_section else status.HTTP_200_OK
        return SubmitQuestionnaireResponse(
            status=True,
            message="Responses processed successfully." + 
                   (" Previous section responses saved to database." if is_changing_section else " Responses stored temporarily."),
            data={},
            status_code=200,
        )

    except Exception as e:
        logger.error(f"Error processing questionnaire response: {str(e)}", exc_info=True)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return SubmitQuestionnaireResponse(
            status=False,
            message=f"Processing failed: {str(e)}",
            data={},
            status_code=500,
        )