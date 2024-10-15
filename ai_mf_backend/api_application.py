import os
import time
import random
import string
import logging

from fastapi import FastAPI, Request
from fastapi.logger import logger as fastapi_logger
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from starlette.middleware.cors import CORSMiddleware

import django
from django.contrib import admin
from django.core.asgi import get_asgi_application





os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "ai_mf_backend.config.v1.django_settings"
)
django.setup()

from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.fastapi_blueprints import connect_router as connect_router_v1

from ai_mf_backend.models.v1.database.user_authentication import (
    UserLogs,
    UserManagement,
)

from ai_mf_backend.utils.v1.errors import (
    InternalServerException,
)
from ai_mf_backend.models.v1.database.user import (
    Gender, MaritalStatus, Occupation, UserPersonalDetails, UserContactInfo, UserOTP, 
    
)
from ai_mf_backend.models.v1.database.financial_details import (
    AnnualIncome, MonthlySavingCapacity, 
    InvestmentAmountPerYear,UserFinancialDetails

)
from ai_mf_backend.models.v1.database.questions import ( Section, Question, Response, UserResponse, ConditionalQuestion
)

from ai_mf_backend.models.v1.database.user_authentication import (
    UserLogs,
    UserManagement,
)
from ai_mf_backend.models.v1.database.mutual_fund import (
    MutualFund,
    HistoricalData,
    PerformanceData,
    TrailingReturn,
    AnnualReturn,
    FundData,
    RiskStatistics,
    FundOverview,
    AMFIMutualFund
)

logger = logging.getLogger(__name__)

fastapi_logger.handlers = logger.handlers

application = FastAPI(title=api_config.PROJECT_NAME)


@application.exception_handler(InternalServerException)
async def internal_server_exception_handler(
    _request: Request, exception: InternalServerException
):
    message = exception.message or "Internal Server Error"
    return JSONResponse(status_code=500, content={"message": message})


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

application.include_router(connect_router_v1, prefix=api_config.API_VER_STR_V1)



@admin.register(UserLogs)
class UserLogsAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'last_access', 'action')
    search_fields = ('user__email', 'device_type', 'action')
    list_filter = ('action', 'device_type')
    ordering = ('-last_access',)


@admin.register(UserManagement)
class UserManagementAdmin(admin.ModelAdmin):
    list_display = ("mobile_number", "email", "created_at")
    search_fields = ("email", "mobile_number")
    list_filter = ("updated_at",)
    ordering = ("-created_at",)


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
    list_display = ('scheme_name', 'q_param', 'created_at', 'updated_at')
    search_fields = ('scheme_name', 'q_param')
    list_filter = ('created_at', 'updated_at')


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
