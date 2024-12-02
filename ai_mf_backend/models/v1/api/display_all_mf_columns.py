from pydantic import BaseModel, Field
from typing import List, Optional


class ResponseModel(BaseModel):
    status: bool
    message: str
    columns: Optional[List[str]] = None
    status_code: int
