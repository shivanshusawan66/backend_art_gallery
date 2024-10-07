from typing import List
from pydantic import BaseModel

# Pydantic models for request/response
class SectionWithQuestion(BaseModel):
    section_id: int
    section_name: str
    question_id: int
    question: str

    class Config:
        orm_mode = True

class UserResponseCreate(BaseModel):
    user_id: int
    question_id: int
    response_id: int
    section_id: int

class UserResponseOut(BaseModel):
    id: int
    user_id: int
    question_id: int
    response_id: int
    section_id: int

class UserResponseInput(BaseModel):
    response_id: int


