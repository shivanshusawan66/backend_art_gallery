from pydantic import BaseModel
from typing import List, Optional


class ResponseModel(BaseModel):
    status: bool
    message: str
    columns: Optional[List[str]] = list()
    status_code: int
