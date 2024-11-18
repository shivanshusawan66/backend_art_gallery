from fastapi import APIRouter, HTTPException, status, Response
from django.core.exceptions import ValidationError
from ai_mf_backend.models.v1.database.user import UserContactInfo
from ai_mf_backend.models.v1.api.saving_responses import SubmitResponseRequest
from ai_mf_backend.models.v1.database.questions import (
    Question, Section, Allowed_Response, UserResponse
)
from asgiref.sync import sync_to_async
from typing import List, Dict

# This will store the responses for each user and section temporarily
user_responses_storage: Dict[int, Dict[int, List[Dict]]] = {}

router = APIRouter()

@router.post("/questionnaire/submit-response-or-section/", status_code=status.HTTP_201_CREATED)
async def submit_response_or_section(
    request: SubmitResponseRequest,
    response: Response
):
    # Fetch user
    user = await sync_to_async(UserContactInfo.objects.filter(user_id=request.user_id).first)()
    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"status": False, "message": "User not found", "status_code": 404}

    # Validate section
    section = await sync_to_async(Section.objects.filter(id=request.section_id).first)()
    if not section:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "status": False,
            "message": f"Section with ID {request.section_id} not found",
            "status_code": 404,
        }

    # Initialize the dictionary for this user if not already initialized
    if request.user_id not in user_responses_storage:
        user_responses_storage[request.user_id] = {}

    # Initialize the list for the current section if not already initialized
    if request.section_id not in user_responses_storage[request.user_id]:
        user_responses_storage[request.user_id][request.section_id] = []

    # Validate each response before temporarily saving it
    for response_item in request.responses:
        question_id = response_item.question_id  # Access using dot notation
        user_response = response_item.response  # Access using dot notation

        # Validate question existence
        question = await sync_to_async(
            Question.objects.filter(id=question_id, section_id=request.section_id).first
        )()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question ID {question_id} not found in section {request.section_id}",
            )

        # Validate allowed response
        allowed_response = await sync_to_async(
            Allowed_Response.objects.filter(question_id=question_id, response=user_response).first
        )()
        if not allowed_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid response '{user_response}' for question {question_id}",
            )

        # Temporarily store the response
        user_responses_storage[request.user_id][request.section_id].append({
            "question_id": question_id,
            "response": user_response,
        })

    # Check if the user is changing the section (has already submitted for a previous section)
    last_section_id = next(iter(user_responses_storage[request.user_id]), None)

    # Save responses for the last section if moving to a new one
    if last_section_id and last_section_id != request.section_id:
        responses = user_responses_storage[request.user_id].pop(last_section_id, [])
        if responses:
            user_responses_to_create: List[UserResponse] = []

            # Validate and prepare responses for saving
            for response_item in responses:
                question_id = response_item["question_id"]
                user_response = response_item["response"]

                allowed_response = await sync_to_async(
                    Allowed_Response.objects.filter(
                        question_id=question_id,
                        response=user_response
                    ).first
                )()
                if not allowed_response:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid response '{user_response}' for question {question_id}",
                    )

                # Create UserResponse instance
                user_response_instance = UserResponse(
                    user_id=request.user_id,
                    question_id=question_id,
                    response_id=allowed_response.id,
                    section_id=last_section_id
                )
                try:
                    # Validate the response
                    await sync_to_async(user_response_instance.full_clean)()
                    user_responses_to_create.append(user_response_instance)
                except ValidationError as e:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail={"errors": e.message_dict},
                    )

            # Save all responses for the last section in bulk
            await sync_to_async(UserResponse.objects.bulk_create)(user_responses_to_create)

    return {"status": True, "message": "Responses temporarily saved. Submit when switching sections."}
