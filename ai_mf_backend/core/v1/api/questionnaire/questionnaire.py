import logging
from typing import List

from asgiref.sync import sync_to_async

from django.db import DatabaseError
from fastapi import APIRouter, Response, Depends, Request

from ai_mf_backend.core.v1.api import limiter

from ai_mf_backend.utils.v1.authentication.secrets import login_checker

from ai_mf_backend.models.v1.api.questionnaire import (
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

from ai_mf_backend.config.v1.api_config import api_config

router = APIRouter()
logger = logging.getLogger(__name__)


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.get(
    "/sections",
    response_model=SectionsResponse,
    dependencies=[Depends(login_checker)],
    status_code=200,
)
async def get_all_sections(request: Request, response: Response):
    try:

        # Fetch sections using async to avoid sync issues
        sections = await sync_to_async(list)(Section.objects.all())

        # Prepare the list of SectionBase objects
        sections_data = [
            SectionBase(section_id=section.pk, section_name=section.section)
            for section in sections
        ]

        # Return success response
        response.status_code = 200
        return SectionsResponse(
            status=True,
            message="Sections fetched successfully.",
            data=sections_data,  # Directly use the list of SectionBase.
            status_code=200,
        )
    except Exception as e:

        logger.error(f"Error fetching sections: {e}")

        # Return error response
        response.status_code = 500
        return SectionsResponse(
            status=False,
            message="Failed to fetch sections.",
            data=None,  # Set data as None for errors
            status_code=500,
        )


@limiter.limit(api_config.REQUEST_PER_MIN)
@router.post(
    "/section-wise-questions/",
    response_model=SectionQuestionsResponse,
    dependencies=[Depends(login_checker)],
    status_code=200,
)
async def get_section_wise_questions(request: SectionRequest, response: Response):
    try:
        # Check if section_id is provided
        specified_section_id = request.section_id
        if specified_section_id is None:
            logger.warning("Section ID is missing or empty.")
            response.status_code = 422
            return SectionQuestionsResponse(
                status=False,
                message="section_id cannot be empty.",
                status_code=422,
            )

        if not isinstance(specified_section_id, int):
            logger.warning(f"Invalid section_id type: {type(specified_section_id)}")
            response.status_code = 422
            return SectionQuestionsResponse(
                status=False,
                message="section_id must be an integer.",
                status_code=422,
            )

        # Fetch the current section using the specified ID

        current_section = await sync_to_async(
            Section.objects.filter(pk=specified_section_id).first
        )()

        if not current_section:
            logger.warning(f"Section ID {specified_section_id} not found.")
            response.status_code = 404
            return SectionQuestionsResponse(
                status=False,
                message="Section not found.",
                status_code=404,
            )

        # Fetch questions associated with the section

        questions = await sync_to_async(list)(
            Question.objects.filter(section=current_section)
        )

        question_data_list: List[QuestionData] = []

        for question in questions:
            options = await sync_to_async(
                lambda: list(
                    Allowed_Response.objects.filter(question=question).values(
                        "id", "response"
                    )
                )
            )()

            conditional_infos = await sync_to_async(
                lambda: list(
                    ConditionalQuestion.objects.filter(question=question).values()
                )
            )()

            visibility_decisions = VisibilityDecisions(if_=[])

            for conditional_info in conditional_infos:
                dependent_question = conditional_info["dependent_question_id"]

                condition_response = await sync_to_async(
                    Allowed_Response.objects.filter(
                        pk=conditional_info["response_id"]
                    ).first
                )()

                condition_value = (
                    condition_response.response if condition_response else None
                )

                # Build visibility condition
                condition = {
                    "value": [condition_value],
                    "show": (
                        [dependent_question]
                        if conditional_info["visibility"] == "show"
                        else []
                    ),
                    "hide": (
                        [dependent_question]
                        if conditional_info["visibility"] == "hide"
                        else []
                    ),
                }

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
            message="Successfully fetched section wise questions and responses",
            data=response_data,
            status_code=200,
        )
    except DatabaseError as db_error:
        logger.error(f"Database error while fetching questions: {str(db_error)}")
        response.status_code = 500
        return SectionQuestionsResponse(
            status=False, message="A database error occurred.", status_code=500
        )

    except Exception as e:
        logger.error(f"Unexpected error while fetching questions: {str(e)}")
        response.status_code = 500
        return SectionQuestionsResponse(
            status=False, message="An unexpected error occurred.", status_code=500
        )
