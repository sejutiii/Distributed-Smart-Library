from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: str
    role: str= "student"

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        orm_mode = True