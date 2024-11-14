from fastapi import APIRouter, HTTPException, status, Response
from django.core.exceptions import ValidationError
from ai_mf_backend.models.v1.database.user import UserContactInfo
from ai_mf_backend.models.v1.api.saving_responses import SubmitResponseRequest
from ai_mf_backend.models.v1.database.questions import (
    Question, Section, Allowed_Response, UserResponse
)
from asgiref.sync import sync_to_async
from typing import List

router = APIRouter()

@router.post("/questionnaire/submit-response/", status_code=status.HTTP_201_CREATED)
async def submit_response(
    request: SubmitResponseRequest,
    response: Response
):
    # Fetch user based on user_id from the request
    user = await sync_to_async(
        UserContactInfo.objects.filter(user_id=request.user_id).first
    )()
    if not user:
        response.status_code = 404
        return {"status": False, "message": "User not found", "status_code": 404}

    # Validate that the section ID exists
    section = await sync_to_async(
        Section.objects.filter(id=request.section_id).first
    )()
    if not section:
        response.status_code = 404
        return {
            "status": False,
            "message": f"Section with ID {request.section_id} not found",
            "status_code": 404,
        }

    # Initialize a list to hold validated UserResponse objects for bulk creation
    user_responses_to_create: List[UserResponse] = []

    # Process each response item for the entire section
    for response_item in request.responses:
        # Validate that the question exists within the section
        question = await sync_to_async(
            Question.objects.filter(id=response_item.question_id, section_id=request.section_id).first
        )()
        if not question:
            response.status_code = 404
            return {
                "status": False,
                "message": f"Question with ID {response_item.question_id} not found in section {request.section_id}",
                "status_code": 404,
            }

        # Validate the response value against allowed responses
        allowed_response = await sync_to_async(
            Allowed_Response.objects.filter(
                question_id=response_item.question_id,
                response=response_item.response
            ).first
        )()
        if not allowed_response:
            response.status_code = 400
            return {
                "status": False,
                "message": f"Invalid response '{response_item.response}' for question {response_item.question_id}",
                "status_code": 400,
            }

        # Prepare a new UserResponse object to save after all validations
        user_response = UserResponse(
            user_id=user.user_id,
            question_id=response_item.question_id,
            response_id=allowed_response.id,
            section_id=request.section_id
        )
        try:
            # Validate each UserResponse instance before saving in bulk
            await sync_to_async(user_response.full_clean)()  # Run validation
            user_responses_to_create.append(user_response)  # Add to batch list if valid
        except ValidationError as e:
            error_details = e.message_dict  # This contains field-specific errors
            response.status_code = 422
            return {
                "status": False,
                "message": "Validation Error",
                "errors": error_details,
                "status_code": 422,
            }

    # Save all validated responses for the section in a single bulk_create operation
    await sync_to_async(UserResponse.objects.bulk_create)(user_responses_to_create)

    # Confirm submission
    return {"status": True, "message": "Responses for section submitted successfully"}
