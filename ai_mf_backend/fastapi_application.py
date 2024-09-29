import time
import random
import string
import logging
from ai_mf_backend.config.v1.asgi import application as django_application
from fastapi import FastAPI, Request
from fastapi.logger import logger as fastapi_logger
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware


from ai_mf_backend.config.v1.api_config import api_config
from ai_mf_backend.core.v1.api.authentication.authentication import (
    router as authentication_router_v1,
)
from ai_mf_backend.core.v1.api.authentication.forget_password import (
    router as forget_password_router_v1,
)
from ai_mf_backend.core.v1.api.authentication.otp_verification import (
    router as otp_verification_router_v1,
)

from ai_mf_backend.utils.v1.errors import (
    InternalServerException,
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

application.include_router(authentication_router_v1)
application.include_router(forget_password_router_v1)
application.include_router(otp_verification_router_v1)
application.mount("/django", django_application)
application.mount(
    "/static", StaticFiles(directory="utils/v1/staticfiles"), name="static"
)


@application.post("/health-check")
def health_check():
    return "AI MF Backend V1 APIs"
