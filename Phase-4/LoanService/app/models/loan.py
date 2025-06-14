from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class LoanStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    book_id = Column(Integer, index=True)
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True))
    return_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(LoanStatus), default=LoanStatus.ACTIVE)