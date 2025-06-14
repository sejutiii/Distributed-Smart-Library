from sqlalchemy import Column, Integer, String, Enum
from app.database import Base
import enum

class Role(enum.Enum):
    student = "student"
    faculty = "faculty"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(Enum(Role), nullable=False)
    books_borrowed = Column(Integer, default=0)
    current_borrows = Column(Integer, default=0)