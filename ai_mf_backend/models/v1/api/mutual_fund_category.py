from pydantic import BaseModel
from typing import List


class Fund(BaseModel):
    id: int
    image: str
    name: str
    desc: str


class FrontendResponse(BaseModel):
    status: bool
    message: str
    data: List[Fund]
    status_code: int
