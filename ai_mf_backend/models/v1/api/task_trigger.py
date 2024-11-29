from pydantic import BaseModel
from pydantic import BaseModel
from typing import List, Optional


class TriggerTaskRequest(BaseModel):
    section_ids: Optional[List[int]] = None


class TaskTriggerResponse(BaseModel):
    success: bool
    message: str
