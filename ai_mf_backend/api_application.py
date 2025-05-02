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
from django.utils.html import format_html
from django.core.asgi import get_asgi_application

from ai_mf_backend.core.v1.api import limiter as rate_limiter

from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.fastapi_blueprints import connect_router as connect_router_v1

from ai_mf_backend.core.v1.tasks.mf_scoring import (
    process_all_schemes,
)
from ai_mf_backend.models.v1.database.contact_message import (
    ContactMessage,
    ContactMessageFundCategory,
)
from ai_mf_backend.models.v1.database.user_authentication import (
    UserLogs,
)

from ai_mf_backend.utils.v1.errors import (
    InternalServerException,
    MalformedJWTRequestException,
    generate_detailed_errors,
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

from ai_mf_backend.models.v1.database.blog import (
    BlogCategory,
    BlogData,
    BlogComment,
    BlogCommentReply,
    BlogCommentReport,
    BlogCommentReportType,
)

from ai_mf_backend.models.v1.database.user_review import UserReview

from ai_mf_backend.models.v1.database.mf_category_wise import (
    MutualFundSubcategory,
    MutualFundType,
)

logger = logging.getLogger(__name__)

fastapi_logger.handlers = logger.handlers

application = FastAPI(title=api_config.PROJECT_NAME)
application.state.limiter = rate_limiter


# @application.on_event("startup")
# async def startup_event():
#     logger.info("Starting up the application...")
#     await process_all_schemes()
#     logger.info("Application started successfully.")


@application.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exception: RateLimitExceeded):
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
    body = await request.body()
    query_params = request.query_params._dict

    detailed_errors = generate_detailed_errors(exc.errors())

    error_response = {
        "status": "error",
        "message": "Validation failed",
        "errors": detailed_errors,
        "request_body": body.decode(),
        "query_params": query_params,
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
    }

    logger.error(f"Validation Error: {error_response}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_response
    )


@application.middleware("http")
async def enforce_json_content_type(request: Request, call_next):
    if request.method in (
        "POST",
        "PUT",
        "PATCH",
    ):  # Only check for methods that typically have a body
        content_type = request.headers.get("Content-Type")
        if content_type != "application/json":
            return JSONResponse(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                content={
                    "status": False,
                    "status_code": 415,
                    "message": "Unsupported Media Type: Please use Content-Type application/json",
                },
            )
    return await call_next(request)


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
application.add_exception_handler(RateLimitExceeded, rate_limit_handler)
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
    list_filter = ("income_category",)
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
        "blogcard_image_preview",
        "add_date",
        "update_date",
    )
    search_fields = (
        "name",
        "user__mobile_number",
    )
    list_filter = (
        "gender",
        "marital_status",
    )
    ordering = ("name",)

    @admin.display(description="User Image Preview")
    def blogcard_image_preview(self, obj):
        if obj.user_image:
            return format_html(
                '<img src="{}" style="max-width:50px; max-height:50px;" />',
                obj.user_image.url,
            )
        return "No Image"


@admin.register(UserContactInfo)
class UserContactInfoAdmin(admin.ModelAdmin):
    list_display = ("email", "mobile_number", "add_date", "update_date")
    search_fields = ("email", "mobile_number")
    ordering = ("email",)


@admin.register(OTPlogs)
class OTPlogsAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "otp_valid", "add_date", "update_date")
    search_fields = ("user__email", "otp")
    list_filter = ("otp_valid", "add_date")
    ordering = ("-add_date",)
    date_hierarchy = "add_date"


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
    search_fields = ("user__email", "user__mobile_number")
    list_filter = (
        "occupation",
        "income_category",
        "saving_category",
        "investment_amount_per_year",
        "regular_source_of_income",
        "lock_in_period_accepted",
        "investment_style",
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
    search_fields = ("question", "section__section")
    list_filter = ("section",)
    ordering = ("section",)


@admin.register(Allowed_Response)
class AllowedResponseAdmin(admin.ModelAdmin):
    list_display = ("question", "section", "response", "add_date", "update_date")
    search_fields = (
        "question__question",
        "response",
    )
    list_filter = ("section",)
    ordering = ("question",)


@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = (
        "user_id",
        "question_id",
        "response_id",
        "section_id",
        "add_date",
        "update_date",
    )
    search_fields = (
        "user_id__email",
        "user_id__mobile_number",
        "question_id__question",
        "response_id__response",
    )
    list_filter = ("section_id", "question_id")
    ordering = ("-add_date",)
    date_hierarchy = "add_date"


@admin.register(ConditionalQuestion)
class ConditionalQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "dependent_question",
        "response",
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
    list_filter = ("action", "device_type", "last_access")
    ordering = ("-last_access",)
    date_hierarchy = "last_access"


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "add_date", "update_date")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(BlogData)
class BlogDataAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "username",
        "category",
        "title",
        "blog_description",
        "created_at",
        "blogcard_image_preview",
    )
    search_fields = (
        "id",
        "title",
        "username",
        "user_id__mobile_number",
        "category__name",
        "blog_description",
    )
    list_filter = ("category", "created_at")
    readonly_fields = ("username", "created_at")
    date_hierarchy = "created_at"

    @admin.display(description="Blog Image Preview")
    def blogcard_image_preview(self, obj):
        if obj.blogcard_image:
            return format_html(
                '<img src="{}" style="max-width:50px; max-height:50px;" />',
                obj.blogcard_image.url,
            )
        return "No Image"


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "blog_post",
        "comment_preview",
        "created_at",
        "updated_at",
        "deleted",
    )
    search_fields = ("username", "content")
    list_filter = ("created_at", "updated_at", "deleted")
    readonly_fields = ("username", "created_at", "updated_at")

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted=False)

    def comment_preview(self, obj):
        if obj.content:
            return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
        return ""

    comment_preview.short_description = "Comment"


@admin.register(BlogCommentReply)
class BlogCommentReplyAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "reply_content",
        "parent_comment_preview",
        "created_at",
        "deleted",
    )
    search_fields = ("username", "content", "parent_comment__content")
    list_filter = ("created_at", "deleted")
    readonly_fields = ("username", "created_at")

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted=False)

    def reply_content(self, obj):
        return (
            obj.content[:50] + "..."
            if obj.content and len(obj.content) > 50
            else obj.content
        )

    reply_content.short_description = "Reply Content"

    def parent_comment_preview(self, obj):
        return (
            obj.parent_comment.content[:50] + "..."
            if obj.parent_comment and len(obj.parent_comment.content) > 50
            else (
                obj.parent_comment.content
                if obj.parent_comment
                else "[Deleted Comment]"
            )
        )

    parent_comment_preview.short_description = "Parent Comment"


@admin.register(BlogCommentReportType)
class BlogCommentReportTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "report_type", "add_date", "update_date")
    search_fields = ("report_type",)
    ordering = ("add_date",)


@admin.register(BlogCommentReport)
class BlogCommentReportAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "comment_content",
        "reply_content",
        "report_type",
        "reported_at",
        "deleted",
    )
    search_fields = ("username", "report_type", "comment__content", "reply__content")
    list_filter = ("report_type", "reported_at", "deleted")
    readonly_fields = ("username", "reported_at")
    list_per_page = 20

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset if request.user.is_superuser else queryset.filter(deleted=False)

    def comment_content(self, obj):
        return (
            (obj.comment.content[:50] + "...")
            if obj.comment and hasattr(obj.comment, "content")
            else "-"
        )

    def reply_content(self, obj):
        return (
            (obj.reply.content[:50] + "...")
            if obj.reply and hasattr(obj.reply, "content")
            else "-"
        )

    comment_content.short_description = "Comment"
    reply_content.short_description = "Reply"


@admin.register(UserReview)
class UserReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "designation",
        "review_title",
        "review_body",
        "number_of_stars",
        "location",
        "user_image_preview",
        "add_date",
        "deleted",
    )
    list_filter = ("number_of_stars", "designation", "location", "add_date")
    search_fields = (
        "username",
        "review_title",
        "review_body",
        "designation",
        "location",
    )
    date_hierarchy = "add_date"

    @admin.display(description="User Image Preview")
    def user_image_preview(self, obj):
        if obj.user_image:
            return format_html(
                '<img src="{}" style="max-width:50px; max-height:50px;" />',
                obj.user_image.url,
            )
        return "No Image"


@admin.register(ContactMessageFundCategory)
class ContactMessageFundCategoryrAdmin(admin.ModelAdmin):
    list_display = ("fund_type", "add_date", "update_date")
    search_fields = ("fund_type",)
    ordering = ("fund_type",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "category_id__fund_type",
        "created_at",
    )
    search_fields = ("first_name", "last_name", "email", "phone_number", "message")
    list_filter = ("category_id", "created_at")


@admin.register(MutualFundType)
class MutualFundTypeAdmin(admin.ModelAdmin):
    list_display = ("fund_type", "add_date", "update_date")
    search_fields = ("fund_type",)
    ordering = ("fund_type",)


@admin.register(MutualFundSubcategory)
class MutualFundSubcategoryAdmin(admin.ModelAdmin):
    list_display = (
        "fund_type_id__fund_type",
        "fund_subcategory",
        "add_date",
        "update_date",
    )
    search_fields = (
        "fund_type_id__fund_type",
        "fund_subcategory",
    )
    list_filter = ("fund_type_id",)
    ordering = ("fund_type_id__fund_type",)


# https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
django_application = get_asgi_application()

application.mount("/django", django_application)

application.mount(
    "/static",
    StaticFiles(directory=os.path.abspath("./ai_mf_backend/utils/v1/staticfiles")),
    name="static",
)

application.mount(
    "/media",
    StaticFiles(directory=os.path.abspath("./ai_mf_backend/utils/v1/mediafiles")),
    name="media",
)


@application.post("/health-check")
def health_check():
    return "AI MF Backend V1 APIs"
