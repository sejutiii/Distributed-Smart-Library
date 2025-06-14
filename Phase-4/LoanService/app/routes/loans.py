from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database import get_db
from app.models.loan import Loan, LoanStatus
from app.schemas.loan import LoanCreate, LoanReturn, LoanResponse, LoanDetailResponse, LoanHistoryResponse, BookDetail, UserDetail
import httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
BOOK_SERVICE_URL = os.getenv("BOOK_SERVICE_URL")

router = APIRouter(prefix="/api", tags=["Loans"])

async def get_user(user_id: int):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{USER_SERVICE_URL}/api/users/{user_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="User not found")
            raise HTTPException(status_code=503, detail="User Service unavailable")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User Service unavailable")

async def get_book(book_id: int):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{BOOK_SERVICE_URL}/api/books/{book_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Book not found")
            raise HTTPException(status_code=503, detail="Book Service unavailable")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Book Service unavailable")

async def update_book_availability(book_id: int, available_copies: int, operation: str):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.patch(
                f"{BOOK_SERVICE_URL}/api/books/{book_id}/availability",
                json={"available_copies": available_copies, "operation": operation}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=503, detail="Book Service unavailable")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Book Service unavailable")

@router.post("/loans", response_model=LoanResponse, status_code=201)
async def issue_book(loan: LoanCreate, db: Session = Depends(get_db)):
    # Validate user
    user = await get_user(loan.user_id)
    # Validate book
    book = await get_book(loan.book_id)
    if book["available_copies"] <= 0:
        raise HTTPException(status_code=400, detail="No available copies of the book")
    # Update book availability
    await update_book_availability(loan.book_id, book["available_copies"] - 1, "decrement")
    # Calculate due date (30 days from now)
    due_date = datetime.utcnow() + timedelta(days=30)
    # Create loan
    new_loan = Loan(user_id=loan.user_id, book_id=loan.book_id, due_date=due_date)
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    return new_loan

@router.post("/returns", response_model=LoanResponse)
async def return_book(return_data: LoanReturn, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == return_data.loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.status == LoanStatus.RETURNED:
        raise HTTPException(status_code=400, detail="Loan already returned")
    loan.status = LoanStatus.RETURNED
    loan.return_date = datetime.utcnow()
    book = await get_book(loan.book_id)
    await update_book_availability(loan.book_id, book["available_copies"] + 1, "increment")
    db.commit()
    db.refresh(loan)
    return loan

@router.get("/loans/user/{user_id}", response_model=LoanHistoryResponse)
async def get_user_loans(user_id: int, db: Session = Depends(get_db)):
    user = await get_user(user_id)
    loans = db.query(Loan).filter(Loan.user_id == user_id).all()
    loan_details = []
    for loan in loans:
        book = await get_book(loan.book_id)
        loan_details.append(LoanDetailResponse(
            id=loan.id,
            user=UserDetail(**user),
            book=BookDetail(**book),
            issue_date=loan.issue_date,
            due_date=loan.due_date,
            return_date=loan.return_date,
            status=loan.status.value
        ))
    return {"loans": loan_details, "total": len(loan_details)}

@router.get("/loans/stats", tags=["Loans"])
def get_loan_stats(db: Session = Depends(get_db)):
    total_loans = db.query(Loan).count()
    active_loans = db.query(Loan).filter(Loan.status == LoanStatus.ACTIVE).count()
    due_today = db.query(Loan).filter(Loan.due_date == datetime.utcnow().date()).count()
    return {"total_loans": total_loans, "active_loans": active_loans, "due_today": due_today}


@router.get("/loans/active-users", tags=["Loans"])
def get_active_users(db: Session = Depends(get_db)):
    active_users = db.query(func.count(func.distinct(Loan.user_id))).filter(Loan.status == LoanStatus.ACTIVE).scalar() or 0
    return {"active_users": active_users}



@router.get("/loans/{id}", response_model=LoanDetailResponse)
async def get_loan(id: int, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    user = await get_user(loan.user_id)
    book = await get_book(loan.book_id)
    return LoanDetailResponse(
        id=loan.id,
        user=UserDetail(**user),
        book=BookDetail(**book),
        issue_date=loan.issue_date,
        due_date=loan.due_date,
        return_date=loan.return_date,
        status=loan.status.value
    )