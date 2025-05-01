from ai_mf_backend.core import connect_router

# Authentication Routers
from ai_mf_backend.core.v1.api.authentication.authentication import (
    router as authentication_router_v1,
)
from ai_mf_backend.core.v1.api.authentication.forget_password import (
    router as forget_password_router_v1,
)
from ai_mf_backend.core.v1.api.authentication.otp_verification import (
    router as otp_verification_router_v1,
)

# User Data Capture Routers
from ai_mf_backend.core.v1.api.user_data_capture.id_options import (
    router as id_options_router_v1,
)
from ai_mf_backend.core.v1.api.user_data_capture.user_personal_financial_detail import (
    router as user_personal_financial_detail_router_v1,
)
from ai_mf_backend.core.v1.api.user_data_capture.display_user_form_responses import (
    router as display_user_form_responses_router_v1,
)

# Questionnaire Routers
from ai_mf_backend.core.v1.api.questionnaire.questionnaire import (
    router as questionnaire_router_v1,
)
from ai_mf_backend.core.v1.api.questionnaire.saving_responses import (
    router as saving_response_router_v1,
)
from ai_mf_backend.core.v1.api.questionnaire.user_response_display import (
    router as questionnaire_user_response_display_v1,
)


from ai_mf_backend.core.v1.api.mf_data.display_mf_each import(
    router as display_mf_each_router_v1,
)

# Display Mutual Fund Data
from ai_mf_backend.core.v1.api.mf_data.display_high_return_mutual_funds import(
    router as display_high_return_mutual_funds_router_v1
)

# MF DATA
from ai_mf_backend.core.v1.api.mf_data.display_mf_recommendations import (
    router as display_mf_recommendations_mutual_funds_router_v1,
)

from ai_mf_backend.core.v1.api.mf_data.display_mf_each import (
    router as display_mf_each_router_v1,
)
from ai_mf_backend.core.v1.api.mf_data.display_mf_filter import(
    router as display_mf_filter_router_v1,
)

from ai_mf_backend.core.v1.api.mf_portfolio.mf_portfolio_section import (
    router as mf_portfolio_section_router_v1,
)

from ai_mf_backend.core.v1.api.mf_data.mf_filter_option_parameters import (
    router as mf_filter_option_parameters_router_v1,   
)


# Blog Data Routers
from ai_mf_backend.core.v1.api.blog.blog_data import (
    router as blog_data_router_v1,
)
from ai_mf_backend.core.v1.api.blog.blog_options import (
    router as blog_options_router_v1,
)
from ai_mf_backend.core.v1.api.blog.blog_comment import (
    router as blog_comment_router_v1,
)
from ai_mf_backend.core.v1.api.blog.blog_comment_reply import (
    router as blog_comment_reply_router_v1,
)
from ai_mf_backend.core.v1.api.blog.blog_comment_report import (
    router as blog_comment_report_router_v1,
)
from ai_mf_backend.core.v1.api.blog.blog_comment_report_options import (
    router as blog_comment_report_options_router_v1,
)

# User Review Routers
from ai_mf_backend.core.v1.api.user_review.user_review import (
    router as user_review_router_v1,
)
from ai_mf_backend.core.v1.api.contact_message.contact_message import (
    router as contact_message_router_v1,
)


# Router Inclusions
connect_router.include_router(authentication_router_v1)
connect_router.include_router(forget_password_router_v1)
connect_router.include_router(otp_verification_router_v1)

connect_router.include_router(id_options_router_v1)
connect_router.include_router(user_personal_financial_detail_router_v1)
connect_router.include_router(display_user_form_responses_router_v1)

connect_router.include_router(questionnaire_router_v1)
connect_router.include_router(saving_response_router_v1)
connect_router.include_router(questionnaire_user_response_display_v1)

connect_router.include_router(display_high_return_mutual_funds_router_v1)
connect_router.include_router(display_mf_recommendations_mutual_funds_router_v1)
connect_router.include_router(display_mf_each_router_v1)
connect_router.include_router(mf_filter_option_parameters_router_v1)
connect_router.include_router(display_mf_filter_router_v1)

connect_router.include_router(mf_portfolio_section_router_v1)

connect_router.include_router(blog_data_router_v1)
connect_router.include_router(blog_comment_router_v1)
connect_router.include_router(blog_options_router_v1)
connect_router.include_router(blog_comment_reply_router_v1)
connect_router.include_router(blog_comment_report_router_v1)
connect_router.include_router(blog_comment_report_options_router_v1)

connect_router.include_router(user_review_router_v1)

connect_router.include_router(contact_message_router_v1)