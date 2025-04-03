from pydantic import BaseModel,field_validator,Field,model_validator
from ai_mf_backend.models.v1.api import Response
from typing import List,Optional,Dict,Any
from asgiref.sync import sync_to_async

class ReportCreateRequest(BaseModel):
    comment_id: Optional[int] = Field(None, gt=0)
    reply_id: Optional[int] = Field(None, gt=0)
    report_type_id: int  

class ReportResponse(Response):
    data:list

class BlogCommentReportOptionResponse(Response):
    pass
