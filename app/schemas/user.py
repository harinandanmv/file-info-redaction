from pydantic import BaseModel, EmailStr
from typing import List

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class RedactionStat(BaseModel):
    date: str
    count: int

class UserStats(BaseModel):
    total_files_redacted: int
    total_entities_detected: int
    most_frequent_entity: str | None
    recent_activity: List[RedactionStat]
