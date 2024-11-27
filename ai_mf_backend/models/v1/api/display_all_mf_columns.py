from pydantic import BaseModel, Field
from typing import List, Optional


class SuccessResponse(BaseModel):
    status: bool = Field(default=True)
    message: str = Field(default="Successfully retrieved references columns")
    columns: List[str]
    status_code: int


class ErrorResponse(BaseModel):
    status: bool = Field(default=False)
    message: str
    status_code: int

    class Config:
        orm_mode = True
