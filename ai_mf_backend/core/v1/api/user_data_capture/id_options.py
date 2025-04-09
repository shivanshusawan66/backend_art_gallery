from fastapi import APIRouter, Response, status
from ai_mf_backend.models.v1.database.financial_details import (
    Occupation,
    AnnualIncome,
    MonthlySavingCapacity,
    InvestmentAmountPerYear,
)

# basically to import questions from questions table for current holding status
from ai_mf_backend.models.v1.database.questions import (
    Question,
    Section,
    Allowed_Response,
)
from ai_mf_backend.models.v1.database.user import Gender, MaritalStatus
from ai_mf_backend.models.v1.api.user_data import (
    UserProfileQuestionResponse,
    UserProfileOptionResponse,
)
from asgiref.sync import sync_to_async

router = APIRouter()


# Function to fetch options for personal details
@router.get("/options_user_personal_details/", response_model=UserProfileOptionResponse)
async def get_personal_options():
    try:
        # Fetching gender and marital status options asynchronously
        genders = await sync_to_async(list)(Gender.objects.all())
        marital_statuses = await sync_to_async(list)(MaritalStatus.objects.all())

        # Formatting the fetched data to match the structure you want
        gender_options = [
            {
                "key": str(gender.id),
                "label": gender.gender,
                "value": gender.gender.lower(),
            }
            for gender in genders
        ]
        marital_status_options = [
            {
                "key": str(status.id),
                "label": status.marital_status,
                "value": status.marital_status.lower(),
            }
            for status in marital_statuses
        ]

        data = {
            "genders": {
                "name": "gender",
                "label": "Gender",
                "options": gender_options,
                "type": "dropdown",
                "default": [gender_options[0]["key"]] if gender_options else [],
                "required": False,
            },
            "marital_statuses": {
                "name": "marital_status",
                "label": "Marital Status",
                "options": marital_status_options,
                "type": "dropdown",
                "default": (
                    [marital_status_options[0]["key"]] if marital_status_options else []
                ),
                "required": False,
            },
        }

        return UserProfileOptionResponse(
            status=True,
            message="Options fetched successfully",
            data=data,
            status_code=200,
        )

    except Exception as e:
        return UserProfileOptionResponse(
            status=False,
            message=f"Failed to fetch options: {str(e)}",
            data={},
            status_code=500,
        )


@router.get(
    "/options_user_financial_details/", response_model=UserProfileOptionResponse
)
async def get_financial_options():
    try:
        # Fetching financial options asynchronously
        occupations = await sync_to_async(list)(Occupation.objects.all())
        annual_incomes = await sync_to_async(list)(AnnualIncome.objects.all())
        monthly_saving_capacities = await sync_to_async(list)(
            MonthlySavingCapacity.objects.all()
        )
        investment_amounts_per_year = await sync_to_async(list)(
            InvestmentAmountPerYear.objects.all()
        )

        # Formatting the fetched data
        occupation_options = [
            {
                "key": str(occupation.id),
                "label": occupation.occupation,
                "value": occupation.occupation.lower(),
            }
            for occupation in occupations
        ]
        annual_income_options = [
            {
                "key": str(income.id),
                "label": income.income_category,
                "value": income.income_category.lower(),
            }
            for income in annual_incomes
        ]
        monthly_saving_capacity_options = [
            {
                "key": str(capacity.id),
                "label": capacity.saving_category,
                "value": capacity.saving_category.lower(),
            }
            for capacity in monthly_saving_capacities
        ]
        investment_amount_per_year_options = [
            {
                "key": str(investment.id),
                "label": investment.investment_amount_per_year,
                "value": investment.investment_amount_per_year.lower(),
            }
            for investment in investment_amounts_per_year
        ]

        data = {
            "occupations": {
                "name": "occupation",
                "label": "Occupation",
                "options": occupation_options,
                "type": "dropdown",
                "default": [occupation_options[0]["key"]] if occupation_options else [],
                "required": False,
            },
            "annual_incomes": {
                "name": "annual_income",
                "label": "Annual Income",
                "options": annual_income_options,
                "type": "dropdown",
                "default": (
                    [annual_income_options[0]["key"]] if annual_income_options else []
                ),
                "required": False,
            },
            "monthly_saving_capacities": {
                "name": "monthly_saving_capacity",
                "label": "Monthly Saving Capacity",
                "options": monthly_saving_capacity_options,
                "type": "dropdown",
                "default": (
                    [monthly_saving_capacity_options[0]["key"]]
                    if monthly_saving_capacity_options
                    else []
                ),
                "required": False,
            },
            "investment_amounts_per_year": {
                "name": "investment_amount_per_year",
                "label": "Investment Amount Per Year",
                "options": investment_amount_per_year_options,
                "type": "dropdown",
                "default": (
                    [investment_amount_per_year_options[0]["key"]]
                    if investment_amount_per_year_options
                    else []
                ),
                "required": False,
            },
        }

        return UserProfileOptionResponse(
            status=True,
            message="Financial options fetched successfully",
            data=data,
            status_code=200,
        )

    except Exception as e:
        return UserProfileOptionResponse(
            status=False,
            message=f"Failed to fetch financial options: {str(e)}",
            data={},
            status_code=500,
        )


@router.get(
    "/options_user_questions_details", response_model=UserProfileQuestionResponse
)
async def get_current_holding_options(response: Response):
    try:
        specified_section_id = 10
        question_ids = [1001, 1002]
        question_labels = {
            1001: "Current Holding in Shares",
            1002: "Current Holding in Mutual Funds",
        }

        current_section = await sync_to_async(
            Section.objects.filter(pk=specified_section_id).first
        )()

        questions = await sync_to_async(list)(
            Question.objects.filter(pk__in=question_ids, section=current_section)
        )

        question_data_list = []
        for question in questions:
            options = await sync_to_async(
                lambda: list(
                    Allowed_Response.objects.filter(question=question).values(
                        "id", "response"
                    )
                )
            )()

            question_data = {
                "question_id": question.pk,
                "name": question_labels.get(question.pk, question.question).lower(),
                "label": question_labels.get(question.pk, question.question),
                "options": [
                    {
                        "key": option["id"],
                        "label": option["response"],
                    }
                    for option in options
                ],
                "required": False,
                "type": "dropdown",
            }
            question_data_list.append(question_data)

        response.status_code = status.HTTP_200_OK
        return UserProfileQuestionResponse(
            status=True,
            message="Successfully fetched option for questions",
            status_code=status.HTTP_200_OK,
            section_id=10,
            data=question_data_list,
        )
    except Exception as e:
        return UserProfileQuestionResponse(
            status=False,
            message=f"Error fetching section questions: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            data=[],
        )
