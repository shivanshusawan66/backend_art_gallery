import logging
from typing import List

from asgiref.sync import sync_to_async

from django.db import DatabaseError
from django.db.models import Count
from django.db.models import Prefetch
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from fastapi import APIRouter, Response, Depends, Request, Header

from ai_mf_backend.core.v1.api import limiter
from ai_mf_backend.utils.v1.authentication.secrets import login_checker
from ai_mf_backend.utils.v1.authentication.validators import (
    custom_validate_international_phonenumber,
)
from ai_mf_backend.utils.v1.authentication.secrets import (
    jwt_token_checker,
    login_checker,
)
from ai_mf_backend.utils.v1.errors import (
    MalformedJWTRequestException,
)
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
    SectionCompletionStatusRequest,
    SectionCompletionStatus,
    SectionCompletionStatusResponse,
)
from ai_mf_backend.models.v1.database.questions import (
    Question,
    Section,
    Allowed_Response,
    ConditionalQuestion,
    UserResponse,
    UserContactInfo
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

        sections = await sync_to_async(list)(Section.objects.all())

        sections_data = [
            SectionBase(section_id=section.pk, section_name=section.section)
            for section in sections
        ]

        # Return success response
        response.status_code = 200
        return SectionsResponse(
            status=True,
            message="Sections fetched successfully.",
            data=sections_data,
            status_code=200,
        )
    except Exception as e:

        logger.error(f"Error fetching sections: {e}")

        response.status_code = 500
        return SectionsResponse(
            status=False,
            message="Failed to fetch sections.",
            data=None,
            status_code=500,
        )

@limiter.limit(api_config.REQUEST_PER_MIN)
@router.post(
    "/section_wise_questions/",
    response_model=SectionQuestionsResponse,
    dependencies=[Depends(login_checker)],
    status_code=200,
)
async def get_section_wise_questions(
    request: SectionRequest,
    response: Response,
    Authorization: str = Header(),  
):
    if not Authorization:
        response.status_code = 422
        return SectionQuestionsResponse(
            status=False,
            message="Authorization header is missing.",
            status_code=422,
        )
    
    try:
        payload = jwt_token_checker(jwt_token=Authorization, encode=False)
    except MalformedJWTRequestException as e:
        response.status_code = 498
        return SectionQuestionsResponse(
            status=False,
            message="Invalid JWT token is provided.",
            status_code=498,
        )

    email = payload.get("email")
    mobile_no = payload.get("mobile_number")

    if not any([email, mobile_no]):
        response.status_code = 422
        return SectionQuestionsResponse(
            status=False,
            message="Invalid JWT token: no email or mobile number found.",
            status_code=422,
        )

    if all([email, mobile_no]):
        response.status_code = 400
        return SectionQuestionsResponse(
            status=False,
            message="Invalid JWT token: both email and mobile number are present.",
            status_code=400,
        )

    if email:
        try:
            _ = validate_email(value=email)
        except ValidationError as error_response:
            response.status_code = 422
            return SectionQuestionsResponse(
                status=False,
                message=f"Invalid email provided: {error_response}",
                status_code=422,
            )

    elif mobile_no:
        try:
            _ = custom_validate_international_phonenumber(value=mobile_no)
        except ValidationError as error_response:
            response.status_code = 422
            return SectionQuestionsResponse(
                status=False,
                message=f"Invalid phone number provided: {error_response}",
                status_code=422,
            )
    user = None
    question_ids = [1001, 1002]
    if email:
        user = await sync_to_async(
            lambda: UserContactInfo.objects.filter(email=email)
            .prefetch_related(
                Prefetch(
                    "userresponse_set",
                    queryset=UserResponse.objects.filter(question_id__in=question_ids).select_related(
                        "question_id", "response_id", "section_id"
                    ),
                )
            )
            .first()
        )()
    elif mobile_no:
        user = await sync_to_async(
            lambda: UserContactInfo.objects.filter(mobile_number=mobile_no)
            .prefetch_related(
                Prefetch(
                    "userresponse_set",
                    queryset=UserResponse.objects.filter(question_id__in=question_ids).select_related(
                        "question_id", "response_id", "section_id"
                    ),
                )
            )
            .first()
        )()

    print(user)
    user_prev_responses = user.userresponse_set.all()
    print(f">>>>>>>>{user_prev_responses}")
    for response in user_prev_responses:
        print(
            f"User ID: {response.user_id.user_id if response.user_id else 'N/A'}, "  
            f"Question ID: {response.question_id.pk if response.question_id else 'N/A'}, " 
            f"Response ID: {response.response_id.pk if response.response_id else 'N/A'}, " 
            f"Section ID: {response.section_id.pk if response.section_id else 'N/A'}, "  
            f"Added on: {response.add_date}, "
            f"Updated on: {response.update_date}"
        )
    if not user:
        response.status_code = 404
        return SectionQuestionsResponse(
            status=False,
            message="User not found.",
            status_code=404,
        )


    try:
        specified_section_id = request.section_id
        if specified_section_id is None:
            logger.warning("Section ID is required.")
            response.status_code = 400
            return SectionQuestionsResponse(
                status=False,
                message="Section ID is required.",
                status_code=400,
            )

        if not isinstance(specified_section_id, int):
            logger.warning(f"Invalid section_id type: {type(specified_section_id)}")
            response.status_code = 422
            return SectionQuestionsResponse(
                status=False,
                message="section_id must be an integer.",
                status_code=422,
            )

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

        questions = await sync_to_async(list)(
            Question.objects.filter(section=current_section)
        )

        question_data_list: List[QuestionData] = []

        for question in questions:
            print(question.pk)
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

                condition_value = {
                    "response_id": (
                        condition_response.pk if condition_response else None
                    ),
                    "response_value": (
                        condition_response.response if condition_response else None
                    ),
                }

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

@router.post(
    "/section_completion_status",
    dependencies=[Depends(login_checker)],
    status_code=200,
)
async def get_section_completion_status(
    request: SectionCompletionStatusRequest,
) -> SectionCompletionStatusResponse:
    try:
        user_id = request.user_id
        if user_id <= 0:
            return SectionCompletionStatusResponse(
                status=False,
                status_code=400,
                message="User_id must be a positive integer",
                data=[],
            )

        sections_with_question_counts = await sync_to_async(
            lambda: list(
                Section.objects.annotate(total_questions=Count("question")).filter(
                    total_questions__gt=0
                )
            )
        )()

        answered_questions_by_section = await sync_to_async(
            lambda: list(
                UserResponse.objects.filter(user_id=user_id, deleted=False)
                .values("section_id")
                .annotate(answered_questions=Count("question_id", distinct=True))
            )
        )()

        answered_questions_dict = {
            item["section_id"]: item["answered_questions"]
            for item in answered_questions_by_section
        }

        section_completion_status = [
            SectionCompletionStatus(
                section_id=section.id,
                section_name=section.section,
                answered_questions=answered_questions_dict.get(section.id, 0),
                total_questions=section.total_questions,
                completion_rate=(
                    round(
                        answered_questions_dict.get(section.id, 0)
                        / section.total_questions
                        * 100,
                        2,
                    )
                    if section.total_questions > 0
                    else 0.0
                ),
            )
            for section in sections_with_question_counts
        ]

        return SectionCompletionStatusResponse(
            status=True,
            message="Successfully fetched section completion data",
            data=section_completion_status,
            status_code=200
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching sections: {str(e)}")
        
        return SectionCompletionStatusResponse(
            status=False, message="An unexpected error occurred.", status_code=500
        )
