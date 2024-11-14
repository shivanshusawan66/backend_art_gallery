from fastapi import APIRouter, HTTPException, status, Response
from django.core.exceptions import ValidationError
from ai_mf_backend.models.v1.database.user import UserContactInfo
from ai_mf_backend.models.v1.api.saving_responses import SubmitResponseRequest
from ai_mf_backend.models.v1.database.questions import (
    Question, Section, Allowed_Response, UserResponse
)
from asgiref.sync import sync_to_async
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/api/questionnaire/submit-response/", status_code=status.HTTP_201_CREATED)
async def submit_response(
    request: SubmitResponseRequest,
    response: Response,
    navigate: str = "submit"  # 'next', 'previous', or 'submit'
):
    # Fetch user based on user_id from the request
    user = await sync_to_async(UserContactInfo.objects.filter(user_id=request.user_id).first)()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Validate that the section ID exists if provided
    section = None
    if request.section_id:
        section = await sync_to_async(Section.objects.filter(id=request.section_id).first)()
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section with ID {request.section_id} not found"
            )

    # Collect responses to save in bulk
    user_responses = []
    for response_item in request.responses:
        # Validate that the question exists
        question = await sync_to_async(Question.objects.filter(id=response_item.question_id).first)()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {response_item.question_id} not found"
            )

        # Validate the response value against allowed responses
        allowed_response = await sync_to_async(
            Allowed_Response.objects.filter(
                question_id=response_item.question_id,
                response=response_item.response
            ).first
        )()
        if not allowed_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid response '{response_item.response}' for question {response_item.question_id}"
            )

        # Prepare validated response for saving
        user_response = UserResponse(
            user_id=user.user_id,
            question_id=response_item.question_id,
            response_id=allowed_response.id,
            section_id=request.section_id
        )
        try:
            await sync_to_async(user_response.full_clean)()  # Run validation
            user_responses.append(user_response)
        except ValidationError as e:
            logger.error(f"Validation Error: {e.message_dict}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"Validation Error": e.message_dict}
            )

    # Save all user responses in bulk
    await sync_to_async(UserResponse.objects.bulk_create)(user_responses)

    # Handle navigation or submission logic
    if navigate == "next":
        next_question = await sync_to_async(
            Question.objects.filter(section_id=request.section_id, id__gt=request.responses[0].question_id).first
        )()
        if next_question:
            return {
                "status": True,
                "message": "Next question",
                "next_question_id": next_question.id,
                "question_text": next_question.question
            }
        else:
            return {
                "status": False,
                "message": "No more questions in this section"
            }

    elif navigate == "previous":
        previous_question = await sync_to_async(
            Question.objects.filter(section_id=request.section_id, id__lt=request.responses[0].question_id).order_by('-id').first
        )()
        if previous_question:
            return {
                "status": True,
                "message": "Previous question",
                "previous_question_id": previous_question.id,
                "question_text": previous_question.question
            }
        else:
            return {
                "status": False,
                "message": "No previous questions in this section"
            }

    # If "submit" is specified or no navigation command, confirm submission
    return {"status": True, "message": "Responses submitted successfully"}
