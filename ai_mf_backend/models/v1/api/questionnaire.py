from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field

from ai_mf_backend.models.v1.api import Response


class Option(BaseModel):
    option_id: int
    response: str


class VisibilityCondition(BaseModel):
    value: List[Dict[str, Union[int, str]]]
    show: Optional[List[int]] = []
    hide: Optional[List[int]] = []


class VisibilityDecisions(BaseModel):
    if_: List[VisibilityCondition] = []


class QuestionData(BaseModel):
    question_id: int
    question: str
    options: List[Option]
    


class SectionBase(BaseModel):
    section_id: int
    section_name: str


class SectionQuestionsData(BaseModel):
    section_id: int
    section_name: str
    questions: List[QuestionData]


class SectionRequest(BaseModel):
    section_id: Optional[int] = Field(
        None, description="The section ID for the request"
    )


class SectionsResponse(Response):
    data: Optional[List[SectionBase]] = None


class SectionQuestionsResponse(Response):
    data: Optional[SectionQuestionsData] = dict()


class SectionCompletionStatusRequest(BaseModel):
    user_id: int = Field(..., description="Unique identifier for the user")


class SectionCompletionStatus(BaseModel):
    section_id: int
    section_name: str
    answered_questions: int
    total_questions: int
    completion_rate: float


class SectionCompletionStatusResponse(Response):
    data: Optional[List[SectionCompletionStatus]] = None
