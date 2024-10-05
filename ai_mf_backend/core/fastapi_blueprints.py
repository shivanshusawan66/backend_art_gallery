from ai_mf_backend.core import connect_router

from ai_mf_backend.core.v1.api.authentication.authentication import (
    router as authentication_router_v1,
)
from ai_mf_backend.core.v1.api.authentication.forget_password import (
    router as forget_password_router_v1,
)
from ai_mf_backend.core.v1.api.authentication.otp_verification import (
    router as otp_verification_router_v1,
)

connect_router.include_router(authentication_router_v1)
connect_router.include_router(forget_password_router_v1)
connect_router.include_router(otp_verification_router_v1)
