from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from ai_mf_backend.models.v1.api import Response


class Option(BaseModel):
    option_id: int
    response: str


class VisibilityCondition(BaseModel):
    value: List[str]
    show: Optional[List[int]] = []
    hide: Optional[List[int]] = []


class VisibilityDecisions(BaseModel):
    if_: List[VisibilityCondition] = []


class QuestionData(BaseModel):
    question_id: int
    question: str
    options: List[Option]
    visibility_decisions: VisibilityDecisions


class SectionBase(BaseModel):
    section_id: int
    section_name: str


class SectionQuestionsData(BaseModel):
    section_id: int
    section_name: str
    questions: List[QuestionData]


class SectionRequest(BaseModel):
    section_id: Optional[str] = Field(
        None, description="The section ID for the request"
    )


class SectionsResponse(Response):
    data: Optional[Dict[str, List[SectionBase]]] = dict()


class SectionQuestionsResponse(Response):
    data: Optional[SectionQuestionsData] = dict()
