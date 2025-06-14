from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict

class LoanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"

class LoanCreate(BaseModel):
    user_id: int
    book_id: int
    due_date: Optional[datetime] = None

class LoanReturn(BaseModel):
    loan_id: int

class LoanExtend(BaseModel):
    extension_days: int

class LoanResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: LoanStatus

    class Config:
        orm_mode = True

class LoanHistoryResponse(BaseModel):
    id: int
    book: Dict
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: LoanStatus

    class Config:
        orm_mode = True

class OverdueLoanResponse(BaseModel):
    id: int
    user: Dict
    book: Dict
    issue_date: datetime
    due_date: datetime
    days_overdue: int

    class Config:
        orm_mode = True

class ExtendedLoanResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    issue_date: datetime
    original_due_date: datetime
    extended_due_date: datetime
    status: LoanStatus
    extensions_count: int

    class Config:
        orm_mode = True

class OverviewStatsResponse(BaseModel):
    total_type_books: int
    total_books: int
    total_users: int
    books_available: int
    books_borrowed: int
    overdue_loans: int
    loans_today: int
    returns_today: int