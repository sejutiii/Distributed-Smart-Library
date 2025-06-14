from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, ActiveUserResponse
from typing import List, Dict

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/active", response_model=List[ActiveUserResponse])
def get_active_users(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.books_borrowed > 0).order_by(User.books_borrowed.desc()).limit(10).all()
    if not users:
        return {"message": "No active users found"}
    return users

@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_total_users(db: Session) -> int:
    return db.query(User).count()

def increment_user_borrows(user_id: int, db: Session) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.current_borrows += 1
    user.books_borrowed += 1
    db.commit()

def decrement_user_borrows(user_id: int, db: Session) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.current_borrows -= 1
    db.commit()

def get_user_details(user_id: int, db: Session) -> Dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.name, "email": user.email}