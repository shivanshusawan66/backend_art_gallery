from pydantic import BaseModel
from typing import List, Optional


class ResponseItem(BaseModel):
    question_id: int
    response: str  # Ensure this attribute exists and is properly defined.


class SubmitResponseRequest(BaseModel):
    user_id: int
    section_id: Optional[int] = None
    responses: List[ResponseItem]  # A list of ResponseItem objects
