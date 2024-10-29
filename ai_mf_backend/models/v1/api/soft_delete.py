from pydantic import BaseModel
from ai_mf_backend.models.v1.api import Response


class soft_delete_and_clone_request(BaseModel):
    model: str
    field_name: str
    record_id: str


class soft_delete_and_clone_response(Response):
    pass


class soft_update_and_clone_request(BaseModel):
    model: str
    field_name: str
    old_record_id: str
    new_record_value: str


class soft_update_and_clone_response(Response):
    pass
