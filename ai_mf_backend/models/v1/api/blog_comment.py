from pydantic import BaseModel
from typing import List
from ai_mf_backend.models.v1.api import Response
from datetime import datetime

class CommentData(BaseModel):
    id:int
    user:str
    content:str
    created_at:datetime

class CommentResponse(Response):
    data: List[CommentData]


class CommentCreateRequest(BaseModel):
    blog_id: int
    content: str

class CommentUpdateRequest(BaseModel):
    comment_id:int
    content: str