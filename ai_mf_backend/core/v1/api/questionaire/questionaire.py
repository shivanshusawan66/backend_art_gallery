import logging
from typing import List, Union
from fastapi import APIRouter, Response
from ai_mf_backend.models.v1.api.questionaire import (
    ErrorResponse,
    Option,
    QuestionData,
    SectionBase,
    SectionQuestionsData,
    SectionQuestionsResponse,
    SectionRequest,
    SectionsResponse,
    VisibilityCondition,
    VisibilityDecisions,
)
from ai_mf_backend.models.v1.database.questions import (
    Question,
    Section,
    Allowed_Response,
    ConditionalQuestion,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/sections", response_model=Union[SectionsResponse, ErrorResponse])
def get_all_sections():
    try:
        sections = Section.objects.all()
        sections_data = [
            SectionBase(section_id=section.pk, section_name=section.section)
            for section in sections
        ]

        # Success response using Pydantic model
        return SectionsResponse(
            status=True,
            message="Sections fetched successfully.",
            data=sections_data,  # Directly use the list of SectionBase.
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Error fetching sections: {e}")

        # Error response using Pydantic model
        return ErrorResponse(
            status=False, message="Failed to fetch sections.", status_code=500
        )


@router.post(
    "/section-wise-questions/",
    response_model=Union[SectionQuestionsResponse, ErrorResponse],
)
def get_section_wise_questions(section_request: SectionRequest, response: Response):
    try:
        # Check if section_id is valid
        specified_section_id = section_request.section_id

        if not specified_section_id:
            logger.warning("Section ID is missing or empty.")
            response.status_code = 422
            return ErrorResponse(
                status=False,
                message="section_id cannot be empty.",
                status_code=422,
            )

        if not isinstance(specified_section_id, str):
            logger.warning(f"Invalid section_id type: {type(specified_section_id)}")
            response.status_code = 422
            return ErrorResponse(
                status=False,
                message="section_id must be a string.",
                status_code=422,
            )

        # Fetch the current section using the specified ID
        current_section = Section.objects.filter(pk=specified_section_id).first()

        if not current_section:
            logger.warning(f"Section ID {specified_section_id} not found.")
            response.status_code = 404
            return ErrorResponse(
                status=False,
                message="Section not found.",
                status_code=404,
            )

        # Fetch questions associated with the section
        questions = Question.objects.filter(section=current_section)
        question_data_list: List[QuestionData] = []

        for question in questions:
            options = Allowed_Response.objects.filter(question=question).values(
                "id", "response"
            )
            conditional_infos = ConditionalQuestion.objects.filter(question=question)

            visibility_decisions = VisibilityDecisions(if_=[])

            for conditional_info in conditional_infos:
                dependent_question = conditional_info.dependent_question
                condition_response = Allowed_Response.objects.filter(
                    pk=conditional_info.response_id
                ).first()

                condition_value = (
                    condition_response.response if condition_response else None
                )

                condition = {
                    "value": [condition_value],
                }

                if conditional_info.visibility == "show":
                    condition["show"] = [dependent_question.id]
                elif conditional_info.visibility == "hide":
                    condition["hide"] = [dependent_question.id]

                visibility_decisions.if_.append(VisibilityCondition(**condition))

            question_data = QuestionData(
                question_id=question.pk,
                question=question.question,
                options=[
                    Option(option_id=option["id"], response=option["response"])
                    for option in options
                ],
                visibility_decisions=visibility_decisions,
            )

            question_data_list.append(question_data)

        response_data = SectionQuestionsData(
            section_id=current_section.pk,
            section_name=current_section.section,
            questions=question_data_list,
        )

        response.status_code = 200
        return SectionQuestionsResponse(
            status=True,
            status_code=200,
            data=response_data,
        )

    except Exception as e:
        logger.error(f"Unexpected error while fetching questions: {str(e)}")
        response.status_code = 500
        return ErrorResponse(status=False, message=str(e), status_code=500)
