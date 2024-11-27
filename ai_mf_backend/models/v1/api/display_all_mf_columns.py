from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class ColumnModel(BaseModel):
    column_name: str = Field(..., description="Name of the column")


class SuccessResponse(BaseModel):
    status: bool = Field(default=True)
    status_code: int = Field()
    message: str = Field(default="Successfully retrieved references")
    columns: List[ColumnModel]


class ErrorResponse(BaseModel):
    status: bool = Field(default=False)
    status_code: int
    message: str
    error_details: Optional[str] = None

    class Config:
        orm_mode = True
