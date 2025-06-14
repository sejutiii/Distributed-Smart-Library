from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class LoanCreate(BaseModel):
    user_id: int
    book_id: int

class LoanReturn(BaseModel):
    loan_id: int

class LoanResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str

    class Config:
        orm_mode = True

class BookDetail(BaseModel):
    id: int
    title: str
    author: str

class UserDetail(BaseModel):
    id: int
    name: str
    email: str

class LoanDetailResponse(BaseModel):
    id: int
    user: UserDetail
    book: BookDetail
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str

class LoanHistoryResponse(BaseModel):
    loans: List[LoanDetailResponse]
    total: int