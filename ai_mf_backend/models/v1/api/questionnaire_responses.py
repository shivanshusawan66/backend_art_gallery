from pydantic import BaseModel
from typing import List

from ai_mf_backend.models.v1.api import Response


class ResponseItem(BaseModel):
    question_id: int
    response_id: int  # Ensure this attribute exists and is properly defined.


class SubmitQuestionnaireRequest(BaseModel):
    user_id: int
    section_id: int
    responses: List[ResponseItem]  # A list of ResponseItem objects


class SubmitQuestionnaireResponse(Response):
    pass
