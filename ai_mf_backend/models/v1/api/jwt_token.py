from pydantic import BaseModel
from typing import Optional
class JWTTokenPayload(BaseModel):
    token_type: str
    creation_time: float
    expiry: float
    email: Optional[str]=None 
    mobile_number: Optional[str]=None 