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

from django.core.asgi import get_asgi_application
from django.contrib import admin
from django.utils.html import format_html

from skti_system_backend.core.v1.api import limiter as rate_limiter
from skti_system_backend.config.v1.api_config import api_config
from skti_system_backend.core.fastapi_blueprints import connect_router as connect_router_v1
from skti_system_backend.utils.v1.errors import (
    InternalServerException,
    MalformedJWTRequestException,
    generate_detailed_errors,
)
from skti_system_backend.models.v1.api.exception_handler import ExceptionHandlerResponse

from skti_system_backend.models.v1.database.gallery import *


# ─────────────────────────────────────────────────────────────────────────────
# Logger setup: route FastAPI’s logger into your handlers
logger = logging.getLogger(__name__)
fastapi_logger.handlers = logger.handlers

# ─────────────────────────────────────────────────────────────────────────────
# Initialize FastAPI
application = FastAPI(title=api_config.PROJECT_NAME)
application.state.limiter = rate_limiter

# ─────────────────────────────────────────────────────────────────────────────
# Exception Handlers

@application.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exception: RateLimitExceeded):
    response = ExceptionHandlerResponse(
        status=False,
        message="Rate limit exceeded. Try again later.",
        data={},
        status_code=429,
    )
    return JSONResponse(content=response.model_dump(), status_code=429)

@application.exception_handler(InternalServerException)
async def internal_error_handler(request: Request, exception: InternalServerException):
    msg = exception.message or "Internal Server Error"
    response = ExceptionHandlerResponse(
        status=False,
        message=f"Failed to initialize the task, Error: {msg}",
        data={},
        status_code=500,
    )
    return JSONResponse(content=response.model_dump(), status_code=500)

@application.exception_handler(MalformedJWTRequestException)
async def malformed_jwt_handler(request: Request, exception: MalformedJWTRequestException):
    return JSONResponse(
        status_code=498,
        content={
            "status": False,
            "message": str(exception),
            "data": {},
            "status_code": 498,
        },
    )

@application.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    errors = generate_detailed_errors(exc.errors())
    payload = {
        "status": "error",
        "message": "Validation failed",
        "errors": errors,
        "request_body": body.decode(),
        "query_params": dict(request.query_params),
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
    }
    logger.error(f"Validation Error: {payload}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=payload,
    )

# ─────────────────────────────────────────────────────────────────────────────
# Middleware

@application.middleware("http")
async def enforce_content_type(request: Request, call_next):
    if request.method in ("POST", "PUT", "PATCH"):
        ct = request.headers.get("Content-Type", "")
        allowed = [
            "application/json",
            "multipart/form-data",
            "image/jpeg",
            "image/png",
            "application/x-www-form-urlencoded",
        ]
        if not any(ct.startswith(a) for a in allowed):
            return JSONResponse(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                content={
                    "status": False,
                    "status_code": 415,
                    "message": "Unsupported Media Type: use JSON, multipart/form-data, or images",
                },
            )
    return await call_next(request)

@application.middleware("http")
async def log_requests(request: Request, call_next):
    rid = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"rid={rid} start path={request.url.path}")
    start = time.time()
    response = await call_next(request)
    ms = (time.time() - start) * 1000
    logger.info(f"rid={rid} completed_in={ms:.2f}ms status={response.status_code}")
    return response

# ─────────────────────────────────────────────────────────────────────────────
# CORS
if api_config.BACKEND_CORS_ORIGINS:
    origins = [o.strip() for o in api_config.BACKEND_CORS_ORIGINS.split(",")]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ─────────────────────────────────────────────────────────────────────────────
# Include your API routes
application.include_router(connect_router_v1, prefix=api_config.API_VER_STR_V1)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'short_description', 'image_preview', 
        'category', 'display_tags', 'is_deleted', 'created_at',
    )
    search_fields = ('title', 'category__name', 'tags__name')
    list_filter = ('is_deleted', 'category', 'tags')
    ordering = ('-created_at',)

    def short_description(self, obj):
        if obj.description:
            return obj.description[:20] + ('...' if len(obj.description) > 20 else '')
        return "-"
    short_description.short_description = 'Description'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 50px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = 'Image Preview'
    image_preview.allow_tags = True

    def display_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())
    display_tags.short_description = 'Tags'






# ─────────────────────────────────────────────────────────────────────────────
# Mount Django ASGI app under /django
django_app = get_asgi_application()
application.mount("/django", django_app)

# ─────────────────────────────────────────────────────────────────────────────
# Static & Media files
application.mount(
    "/static",
    StaticFiles(directory=os.path.abspath("./skti_system_backend/utils/v1/staticfiles")),
    name="static",
)
application.mount(
    "/media",
    StaticFiles(directory=os.path.abspath("./skti_system_backend/utils/v1/mediafiles")),
    name="media",
)

# ─────────────────────────────────────────────────────────────────────────────
# Health‑check (GET)
@application.get("/health-check")
def health_check():
    return {"status": "OK", "service": api_config.PROJECT_NAME}
