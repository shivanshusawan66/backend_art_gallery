from typing import Optional

from pydantic import BaseModel
from ai_mf_backend.models.v1.api import Response


class ContactMessageRequest(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: str
    phone_number: str
    category_id: int
    message: Optional[str] = None


class ContactMessageResponse(Response):
    pass


class ContactMessageFundCategoryOptionResponse(Response):
    pass
