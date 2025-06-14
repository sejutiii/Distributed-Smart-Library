from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
import httpx
from dotenv import load_dotenv
import os

load_dotenv()
LOAN_SERVICE_URL = os.getenv("LOAN_SERVICE_URL")

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

@router.get("/stats", tags=["Users"])
async def get_user_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    # Fetch active users by querying Loan Service for users with active loans
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            # We'll need a new endpoint in Loan Service to get distinct users with active loans
            response = await client.get(f"{LOAN_SERVICE_URL}/api/loans/active-users")
            response.raise_for_status()
            active_users = response.json().get("active_users", 0)
        except (httpx.HTTPStatusError, httpx.RequestError):
            # If Loan Service is unavailable, return 0 for active_users
            active_users = 0
    return {"users": total_users, "active_users": active_users}



@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{id}", response_model=UserResponse)
def update_user(id: int, user_update: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user_update.dict().items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

