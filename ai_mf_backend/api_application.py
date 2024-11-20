import os
import time
import random
import string
import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.logger import logger as fastapi_logger
from fastapi.staticfiles import StaticFiles

from slowapi.errors import RateLimitExceeded

from starlette.middleware.cors import CORSMiddleware

from django.contrib import admin
from django.core.asgi import get_asgi_application

from ai_mf_backend.core.v1.api import limiter as rate_limiter

from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.fastapi_blueprints import connect_router as connect_router_v1

from ai_mf_backend.models.v1.database.user_authentication import (
    UserLogs,
)

from ai_mf_backend.utils.v1.errors import (
    InternalServerException,
    MalformedJWTRequestException,
)
from fastapi.exception_handlers import (
    request_validation_exception_handler as _request_validation_exception_handler,
)
from ai_mf_backend.models.v1.api.exception_handler import ExceptionHandlerResponse
from ai_mf_backend.models.v1.database.user import (
    Gender,
    MaritalStatus,
    Occupation,
    UserPersonalDetails,
    UserContactInfo,
    OTPlogs,
)
from ai_mf_backend.models.v1.database.financial_details import (
    AnnualIncome,
    MonthlySavingCapacity,
    InvestmentAmountPerYear,
    UserFinancialDetails,
)
from ai_mf_backend.models.v1.database.questions import (
    Section,
    Question,
    Allowed_Response,
    UserResponse,
    ConditionalQuestion,
)

from ai_mf_backend.models.v1.database.user_authentication import UserLogs
from ai_mf_backend.models.v1.database.mutual_fund import (
    MutualFund,
    HistoricalData,
    PerformanceData,
    TrailingReturn,
    AnnualReturn,
    FundData,
    RiskStatistics,
    FundOverview,
    AMFIMutualFund,
)

logger = logging.getLogger(__name__)

fastapi_logger.handlers = logger.handlers

application = FastAPI(title=api_config.PROJECT_NAME)
application.state.limiter = rate_limiter


@application.exception_handler(RateLimitExceeded)
async def rate_limit_handler(_request: Request, exception: RateLimitExceeded):
    api_response = ExceptionHandlerResponse(
        status=False,
        message="Rate limit exceeded. Try again later.",
        data={},
        status_code=429,
    )

    return JSONResponse(
        content=api_response.model_dump(), status_code=api_response.status_code
    )


@application.exception_handler(InternalServerException)
async def internal_server_exception_handler(
    _request: Request, exception: InternalServerException
):
    message = exception.message or "Internal Server Error"
    api_response = ExceptionHandlerResponse(
        status=False,
        status_code=500,
        message=f"Failed to initialize the task, Error: {message}",
        data={},
    )

    return JSONResponse(
        content=api_response.model_dump(), status_code=api_response.status_code
    )


@application.exception_handler(MalformedJWTRequestException)
async def malformed_jwt_exception_handler(
    request: Request, exc: MalformedJWTRequestException
):
    return JSONResponse(
        status_code=498,
        content={
            "status": False,
            "message": str(exc),
            "data": {},
            "status_code": 498,
        },
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    This is a wrapper to the default RequestValidationException handler of FastAPI.
    This function will be called when client input is not valid.
    """
    logger.debug("Our custom request_validation_exception_handler was called")
    body = await request.body()
    query_params = request.query_params._dict  # pylint: disable=protected-access

    detail = [
        {
            "type": "missing",
            "loc": ["body", field["loc"][-1]],  # Get the field name from the location
            "msg": f"{field['loc'][-1].replace('_', ' ').capitalize()} is required",  # Custom error message
            "input": {},  # No input, as the field is missing
        }
        for field in exc.errors()
        if isinstance(field, dict) and field.get("msg") == "Field required"
    ]
    detail = {"errors": detail, "body": body.decode(), "query_params": query_params}
    logger.info(detail)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": detail},
    )


@application.middleware("http")
async def log_requests(request: Request, call_next):
    idem = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()

    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    logger.info(
        f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}"
    )

    return response


if api_config.BACKEND_CORS_ORIGINS:
    logger.info("Adding CORS Origins")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin) for origin in api_config.BACKEND_CORS_ORIGINS.split(",")
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
application.add_exception_handler(
    RequestValidationError, request_validation_exception_handler
)
application.include_router(connect_router_v1, prefix=api_config.API_VER_STR_V1)


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ("gender", "add_date", "update_date")
    search_fields = ("gender",)
    ordering = ("gender",)


@admin.register(MaritalStatus)
class MaritalStatusAdmin(admin.ModelAdmin):
    list_display = ("marital_status", "add_date", "update_date")
    search_fields = ("marital_status",)
    ordering = ("marital_status",)


@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    list_display = ("occupation", "add_date", "update_date")
    search_fields = ("occupation",)
    ordering = ("occupation",)


@admin.register(AnnualIncome)
class AnnualIncomeAdmin(admin.ModelAdmin):
    list_display = ("income_category", "add_date", "update_date")
    search_fields = ("income_category",)
    ordering = ("income_category",)


@admin.register(MonthlySavingCapacity)
class MonthlySavingCapacityAdmin(admin.ModelAdmin):
    list_display = ("saving_category", "add_date", "update_date")
    search_fields = ("saving_category",)
    ordering = ("saving_category",)


@admin.register(InvestmentAmountPerYear)
class InvestmentAmountPerYearAdmin(admin.ModelAdmin):
    list_display = ("investment_amount_per_year", "add_date", "update_date")
    search_fields = ("investment_amount_per_year",)
    ordering = ("investment_amount_per_year",)


@admin.register(UserPersonalDetails)
class UserPersonalDetailsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "date_of_birth",
        "gender",
        "marital_status",
        "add_date",
        "update_date",
    )
    search_fields = ("name",)
    list_filter = ("gender", "marital_status")
    ordering = ("name",)


@admin.register(UserContactInfo)
class UserContactInfoAdmin(admin.ModelAdmin):
    list_display = ("email", "mobile_number", "add_date", "update_date")
    search_fields = ("email", "mobile_number")
    ordering = ("email",)


@admin.register(OTPlogs)
class OTPlogsAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "otp_valid", "add_date", "update_date")
    search_fields = ("user__email", "otp")
    ordering = ("-add_date",)


@admin.register(UserFinancialDetails)
class UserFinancialDetailsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "occupation",
        "income_category",
        "saving_category",
        "investment_amount_per_year",
        "regular_source_of_income",
        "lock_in_period_accepted",
        "investment_style",
        "add_date",
        "update_date",
    )
    search_fields = ("user__email",)
    list_filter = (
        "occupation",
        "income_category",
        "saving_category",
        "investment_amount_per_year",
    )
    ordering = ("user",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("section", "add_date", "update_date")
    search_fields = ("section",)
    ordering = ("section",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("section", "question", "add_date", "update_date")
    search_fields = ("question",)
    list_filter = ("section",)
    ordering = ("section",)


@admin.register(Allowed_Response)
class AllowedResponseAdmin(admin.ModelAdmin):
    list_display = ("question", "section", "response", "add_date", "update_date")
    search_fields = ("response",)
    list_filter = ("section", "question")
    ordering = ("question",)


@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "question",
        "response",
        "section",
        "add_date",
        "update_date",
    )
    search_fields = ("user__email", "question__question")
    list_filter = ("section", "question")
    ordering = ("user",)


@admin.register(ConditionalQuestion)
class ConditionalQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "dependent_question",
        "condition",
        "visibility",
        "add_date",
        "update_date",
    )
    search_fields = ("question__question", "dependent_question__question")
    list_filter = ("visibility",)
    ordering = ("question",)


@admin.register(UserLogs)
class UserLogsAdmin(admin.ModelAdmin):
    list_display = ("user", "device_type", "last_access", "action")
    search_fields = ("user__email", "device_type", "action")
    list_filter = ("action", "device_type")
    ordering = ("-last_access",)


@admin.register(MutualFund)
class MutualFundAdmin(admin.ModelAdmin):
    list_display = ("scheme_name", "symbol", "net_asset_value", "date")
    search_fields = ("scheme_name", "symbol")
    list_filter = ("date",)


@admin.register(HistoricalData)
class HistoricalDataAdmin(admin.ModelAdmin):
    list_display = ("fund", "date", "open", "close", "volume")
    list_filter = ("fund", "date")
    date_hierarchy = "date"


@admin.register(PerformanceData)
class PerformanceDataAdmin(admin.ModelAdmin):
    list_display = (
        "fund",
        "morningstar_return_rating",
        "ytd_return",
        "average_return_5y",
    )
    list_filter = ("morningstar_return_rating",)


@admin.register(TrailingReturn)
class TrailingReturnAdmin(admin.ModelAdmin):
    list_display = ("fund", "metric", "fund_return", "benchmark_return")
    list_filter = ("metric", "fund")


@admin.register(AnnualReturn)
class AnnualReturnAdmin(admin.ModelAdmin):
    list_display = ("fund", "year", "fund_return", "category_return")
    list_filter = ("year", "fund")


@admin.register(FundData)
class FundDataAdmin(admin.ModelAdmin):
    list_display = ("fund", "min_initial_investment", "min_subsequent_investment")


@admin.register(RiskStatistics)
class RiskStatisticsAdmin(admin.ModelAdmin):
    list_display = ("fund", "period", "alpha", "beta", "sharpe_ratio")
    list_filter = ("period", "fund")


@admin.register(FundOverview)
class FundOverviewAdmin(admin.ModelAdmin):
    list_display = (
        "fund",
        "category",
        "fund_family",
        "net_assets",
        "ytd_return",
        "yield_value",
        "morningstar_rating",
        "inception_date",
    )
    search_fields = ("fund__scheme_name", "category", "fund_family")
    list_filter = ("category", "fund_family")


@admin.register(AMFIMutualFund)
class AMFIMutualFundAdmin(admin.ModelAdmin):
    list_display = ("scheme_name", "q_param", "created_at", "updated_at")
    search_fields = ("scheme_name", "q_param")
    list_filter = ("created_at", "updated_at")


# https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
django_application = get_asgi_application()

application.mount("/django", django_application)

application.mount(
    "/static",
    StaticFiles(directory=os.path.abspath("./ai_mf_backend/utils/v1/staticfiles")),
    name="static",
)


@application.post("/health-check")
def health_check():
    return "AI MF Backend V1 APIs"
