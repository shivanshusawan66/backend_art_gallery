from pydantic import BaseModel
from typing import List, Optional


class FundCategory(BaseModel):
    id: int
    image: str
    name: str
    desc: str


class FrontendResponse(BaseModel):
    status: bool
    message: str
    data: Optional[List[FundCategory]] = None
    status_code: int


class ErrorResponse(BaseModel):
    status: bool
    message: str
    data: Optional[None] = None
    status_code: int
