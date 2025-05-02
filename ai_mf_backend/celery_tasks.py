import logging

from ai_mf_backend.core import celery_app

from ai_mf_backend.core.v1.tasks.questionnaire_scoring import (
    assign_final_question_weights,
    assign_final_section_weights,
)

from ai_mf_backend.core.v1.tasks.mf_scoring import (
    assign_final_marker_weights,
    assign_final_section_weights_for_mutual_funds,
)

from ai_mf_backend.core.v1.tasks.fetching_data import (
    fetch_and_store_api_data,
    run_all_apis,
)

logger = logging.getLogger(__name__)

__all__ = [
    "assign_final_question_weights",
    "assign_final_section_weights",
    "assign_final_marker_weights",
    "assign_final_section_weights_for_mutual_funds",
    "fetch_and_store_api_data",
    "run_all_apis",
]
