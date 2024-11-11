from typing import List
from pydantic import BaseModel


class SectionRequest(BaseModel):
    section_id: int
