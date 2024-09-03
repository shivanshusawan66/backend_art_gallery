from typing import Dict, Optional

from pydantic import BaseModel


class Response(BaseModel):
    status: bool
    message: str
    data: Dict
    status_code: Optional[int] = 200
