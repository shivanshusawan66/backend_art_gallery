import logging
from django.db import DatabaseError
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from ai_mf_backend.models.v1.api.questionaire import SectionRequest
from ai_mf_backend.models.v1.database.questions import (
    Question,
    Section,
    Allowed_Response,
    ConditionalQuestion,
)

router = APIRouter()
logger = logging.getLogger(__name__)


# GET endpoint to fetch all sections without questions
@router.get("/sections")
def get_all_sections():
    try:
        # Fetch all sections
        sections = Section.objects.all()
        # Structure the response to include only sections
        sections_data = [
            {"section_id": section.pk, "section_name": section.section_name}
            for section in sections
        ]
        return JSONResponse({"data": sections_data})
    except Exception as e:
        logger.error(f"Error fetching sections: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sections.")

@router.post("/section-wise-questions/")
def get_section_wise_questions(section_request: SectionRequest):
    try:
        specified_section_id = section_request.section_id
        current_section = Section.objects.filter(pk=specified_section_id).first()
        
        if not current_section:
            return JSONResponse(
                status_code=404,
                content={
                    "status_code": 404,
                    "detail": "Section not found."
                }
            )

        questions = Question.objects.filter(section=current_section)
        question_data_list = []

        for question in questions:
            options = Allowed_Response.objects.filter(question=question).values("id", "response")
            conditional_infos = ConditionalQuestion.objects.filter(question=question)

            # Initialize visibility decisions
            visibility_decisions = {"if_": []}

            if conditional_infos.exists():
                for conditional_info in conditional_infos:
                    dependent_question = conditional_info.dependent_question
                    condition_response = Allowed_Response.objects.filter(pk=conditional_info.condition_id).first()

                    condition_value = condition_response.response if condition_response else None

                    if conditional_info.visibility == "show":
                        visibility_decisions["if_"].append({
                            "value": [condition_value],
                            "show": [dependent_question.id],
                        })
                    elif conditional_info.visibility == "hide":
                        visibility_decisions["if_"].append({
                            "value": [condition_value],
                            "hide": [dependent_question.id],
                        })

            question_data = {
                "question_id": question.pk,
                "question": question.question,
                "options": [{"option_id": option["id"], "response": option["response"]} for option in options],
                "visibility_decisions": visibility_decisions,
            }

            question_data_list.append(question_data)

        return JSONResponse(
            status_code=200,
            content={
                "status_code": 200,
                "data": {
                    "section_id": current_section.pk,
                    "section_name": current_section.section_name,
                    "questions": question_data_list,
                }
            }
        )
    except DatabaseError:  # Specify the exception
        return JSONResponse(
            status_code=500,
            content={
                "status_code": 500,
                "detail": "Database error"
            }
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Unexpected error: {str(e)}")  # Consider using logging instead
        return JSONResponse(
            status_code=500,
            content={
                "status_code": 500,
                "detail": str(e)
            }
        )
