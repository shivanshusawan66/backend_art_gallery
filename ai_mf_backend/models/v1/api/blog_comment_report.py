from pydantic import BaseModel,field_validator,Field,model_validator
from ai_mf_backend.models.v1.api import Response
from typing import List,Optional,Dict,Any
from ai_mf_backend.models.v1.database.blog import BlogCommentReportType

class ReportCreateRequest(BaseModel):
    comment_id: Optional[int] = Field(None, gt=0)  
    reply_id: Optional[int] = Field(None, gt=0)    
    report_type: str

    @model_validator(mode="after")
    def check_exclusive_fields(cls, model: "ReportCreateRequest") -> "ReportCreateRequest":
        if (model.comment_id is None and model.reply_id is None) or (model.comment_id is not None and model.reply_id is not None):
            raise ValueError("Provide exactly one of comment_id or reply_id.")
        return model

    @field_validator('report_type')
    def validate_report_type(cls, v: str) -> str:
        valid_choices = [choice.value for choice in BlogCommentReportType]
        if v not in valid_choices:
            raise ValueError(f"Invalid report type: {v}. Use one of {valid_choices}")
        return v
    
class ReportResponse(Response):
    data:list
