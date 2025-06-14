from pydantic import BaseModel
from datetime import datetime
from typing import List

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    copies: int

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    copies: int
    available_copies: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        orm_mode = True

class BookAvailabilityUpdate(BaseModel):
    available_copies: int
    operation: str

class BookSearchResponse(BaseModel):
    books: List[BookResponse]
    total: int
    page: int
    per_page: int