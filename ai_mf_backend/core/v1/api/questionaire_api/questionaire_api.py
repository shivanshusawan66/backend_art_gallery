import uuid
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.schemas.v1.questionaire_api import UserResponseInput
from app.models import Question, Section, Response, UserPersonalDetails, UserResponse

router = APIRouter()

# Helper function to get or create session ID
def get_session_id(request: Request):
    return request.headers.get('session_id', str(uuid.uuid4()))

# GET endpoint to fetch the next question along with options
@router.get("/questions/next")
def get_next_question(request: Request):
    session_id = get_session_id(request)

    try:
        # Default user_id = 1 if not passed in the request headers
        user_id = request.headers.get("user_id", 1)
        user = UserPersonalDetails.objects.get(pk=user_id)

        # Fetch the latest user response or default to the first section and question
        last_response = UserResponse.objects.filter(user=user).order_by("-id").first()

        if last_response:
            # Get the next question in the same section or move to the next section
            next_question = Question.objects.filter(
                section=last_response.section, id__gt=last_response.question.pk
            ).first()
        else:
            # Start from the first section and first question if no response exists
            first_section = Section.objects.first()
            next_question = Question.objects.filter(section=first_section).first()

        if not next_question:
            return JSONResponse({
                "session_id": session_id,
                "message": "No more questions available"
            })

        # Fetch the options (responses) for the next question
        options = Response.objects.filter(question=next_question).values('id', 'response')

        # Return the next question data along with options
        return JSONResponse({
            "session_id": session_id,
            "data": {
                "question_id": next_question.pk,
                "question": next_question.question,
                "section_id": next_question.section.pk,
                "section_name": next_question.section.section_name,
                "options": [{"option_id": option['id'], "response": option['response']} for option in options]
            }
        })

    except UserPersonalDetails.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

# POST endpoint to save user's response
@router.post("/user-responses/")
def create_user_response(user_response: UserResponseInput, request: Request):
    session_id = get_session_id(request)

    try:
        # Default user_id = 1 if not passed in the request headers
        user_id = request.headers.get("user_id", 1)
        user = UserPersonalDetails.objects.get(pk=user_id)

        # Fetch the latest question answered by the user
        last_response = UserResponse.objects.filter(user=user).order_by("-id").first()

        if last_response:
            # Get the current question in the same section or move to the next section
            current_question = Question.objects.filter(
                section=last_response.section, id__gt=last_response.question.pk
            ).first()
        else:
            # Start from the first question of the first section if no previous response
            first_section = Section.objects.first()
            current_question = Question.objects.filter(section=first_section).first()

        if not current_question:
            raise HTTPException(status_code=404, detail="No question found to answer")

        # Validate that the response corresponds to the current question
        response = Response.objects.filter(pk=user_response.response_id, question=current_question).first()
        if not response:
            raise HTTPException(status_code=404, detail="Invalid response")

        # Save the user's response
        UserResponse.objects.create(
            user=user,
            question=current_question,
            response=response,
            section=current_question.section
        )

        # Fetch the next question after saving the response
        next_question = Question.objects.filter(
            section=current_question.section, id__gt=current_question.pk
        ).first()

        # If no next question in the current section, move to the next section
        if not next_question:
            next_question = Question.objects.filter(section__pk__gt=current_question.section.pk).first()

        # Check if there are no more questions left in any section
        if not next_question:
            return JSONResponse({
                "session_id": session_id,
                "message": "Well done! You have completed all questions.",
            })

        # Fetch the options for the next question
        options = Response.objects.filter(question=next_question).values('id', 'response')

        # Success response after saving the user response
        return JSONResponse({
            "session_id": session_id,
            "message": "Your response has been saved.",
            "next_question": {
                "question_id": next_question.pk,
                "question": next_question.question,
                "section_id": next_question.section.pk,
                "section_name": next_question.section.section_name,
                "options": [{"option_id": option['id'], "response": option['response']} for option in options]
            }
        })

    except UserPersonalDetails.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except (Question.DoesNotExist, Response.DoesNotExist, Section.DoesNotExist) as e:
        raise HTTPException(status_code=404, detail=str(e))
 