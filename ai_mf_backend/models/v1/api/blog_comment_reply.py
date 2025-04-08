from pydantic import BaseModel
from typing import List
from ai_mf_backend.models.v1.api import Response
from datetime import datetime


class CommentReplyData(BaseModel):
    id: int
    user: str
    content: str
    created_at: datetime


class CommentReplyResponse(Response):
    data: List[CommentReplyData]


class CommentReplyCreateRequest(BaseModel):
    comment_id: int
    content: str
