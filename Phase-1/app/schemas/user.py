from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

class Role(str, Enum):
    student = "student"
    faculty = "faculty"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: Role

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role

    class Config:
        orm_mode = True

class ActiveUserResponse(BaseModel):
    id: int
    name: str
    books_borrowed: int
    current_borrows: int

    class Config:
        orm_mode = True