from fastapi import APIRouter,Response,Header,Depends
from asgiref.sync import sync_to_async
from ai_mf_backend.models.v1.database.questions import UserResponse
from ai_mf_backend.models.v1.database.user import UserContactInfo
from ai_mf_backend.utils.v1.authentication.secrets import login_checker
from ai_mf_backend.models.v1.api.questionnaire_responses import UserQuestionnaireResponse
from django.forms.models import model_to_dict
from typing import Optional
from django.db import DatabaseError

router=APIRouter()

@router.get(
    "/user_questionnaire_response/{user_id}",
    response_model=UserQuestionnaireResponse,
    dependencies=[Depends(login_checker)],
)
async def get_user_personal_financial_details(
    user_id: int,
    response: Response,
    Authorization: Optional[str] = Header(None),  # Optional header
):
    try:
        # Fetch user contact info
        user = await sync_to_async(
            UserContactInfo.objects.filter(user_id=user_id).first
        )()

        if not user:
            response.status_code = 404
            return UserQuestionnaireResponse(
                status=False,
                message="User is not registered with the platform yet.",
                data={},
                status_code=404,
            )

        # Fetch user responses
        user_responses = await sync_to_async(
            UserResponse.objects.filter(user_id=user_id)
            .select_related('question_id', 'response_id', 'section_id')
            .all()
        )()

        if not user_responses:
            response.status_code = 404
            return UserQuestionnaireResponse(
                status=False,
                message="No user responses found.",
                data={},
                status_code=404,
            )

        # Organize responses by section and question
        data = {}
        for user_response in user_responses:
            # Check if section and question exist
            if not user_response.section_id or not user_response.question_id:
                continue

            section_name = user_response.section_id.name
            question_text = user_response.question_id.question
            response_text = user_response.response_id.response if user_response.response_id else None

            # Group responses by section
            if section_name not in data:
                data[section_name] = {}

            data[section_name][question_text] = response_text

        return UserQuestionnaireResponse(
            status=True,
            message="Fetched user responses successfully.",
            data=data,
            status_code=200,
        )

    except DatabaseError as db_err:
        # Handle database errors
        response.status_code = 500
        return UserQuestionnaireResponse(
            status=False,
            message=f"A database error occurred: {str(db_err)}",
            data={},
            status_code=500,
        )
    except Exception as e:
        # General exception handling for any other issues
        return UserQuestionnaireResponse(
            status=False,
            message=f"An unexpected error occurred: {str(e)}",
            data={},
            status_code=500,
        )