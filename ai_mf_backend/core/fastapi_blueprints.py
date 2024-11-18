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
from ai_mf_backend.core.v1.api.user_data_capture.id_options import (
    router as id_options_router_v1,
)
from ai_mf_backend.core.v1.api.user_data_capture.user_personal_financial_detail import (
    router as user_personal_financial_detail_router_v1,
)
from ai_mf_backend.core.v1.api.yf_data_pull.yf_data_pull import (
    router as yf_data_pull_router_v1,
)
from ai_mf_backend.core.v1.api.questionaire.questionaire import (
    router as questionaire_router_v1,
)
from ai_mf_backend.core.v1.api.amfi_parsers.amfi_parser import (
    router as amfi_parser_router_v1,
)
from ai_mf_backend.core.v1.api.display_mf_data.display_mf_data import (
    router as display_mf_data_router_v1,
)
from ai_mf_backend.core.v1.api.soft_delete.soft_delete import (
    router as soft_delete_router,
)

from ai_mf_backend.core.v1.api.questionnaire.saving_responses import (
    router as saving_response_v1,
)

connect_router.include_router(authentication_router_v1)
connect_router.include_router(forget_password_router_v1)
connect_router.include_router(otp_verification_router_v1)
connect_router.include_router(id_options_router_v1)
connect_router.include_router(user_personal_financial_detail_router_v1)
connect_router.include_router(yf_data_pull_router_v1)
connect_router.include_router(questionaire_router_v1)
connect_router.include_router(amfi_parser_router_v1)
connect_router.include_router(display_mf_data_router_v1)
connect_router.include_router(soft_delete_router)
connect_router.include_router(saving_response_v1)
