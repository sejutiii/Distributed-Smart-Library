from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class LoanStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=True)
    status = Column(Enum(LoanStatus), default=LoanStatus.ACTIVE)
    extensions_count = Column(Integer, default=0)

    user = relationship("User")
    book = relationship("Book")