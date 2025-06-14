from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.loan import Loan, LoanStatus
from app.schemas.loan import LoanCreate, LoanReturn, LoanExtend, LoanResponse, LoanHistoryResponse, OverdueLoanResponse, ExtendedLoanResponse, OverviewStatsResponse
from app.routes.users import get_total_users, increment_user_borrows, decrement_user_borrows, get_user_details
from app.routes.books import get_total_books, get_total_type_books ,get_books_available, get_books_borrowed, check_book_availability, borrow_book, return_book_to_inventory, get_book_details
from datetime import datetime, timedelta
from typing import List

router = APIRouter(prefix="/api", tags=["Loans", "Stats"])

@router.post("/loans/", response_model=LoanResponse, status_code=201)
def issue_book(loan: LoanCreate, db: Session = Depends(get_db)):
    check_book_availability(loan.book_id, db)
    borrow_book(loan.book_id, db)
    increment_user_borrows(loan.user_id, db)
    
    due_date = loan.due_date or (datetime.utcnow() + timedelta(days=30))
    
    new_loan_data = loan.dict()
    new_loan_data['due_date'] = due_date
    
    new_loan = Loan(**new_loan_data)
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    return new_loan

@router.post("/returns/", response_model=LoanResponse)
def return_book(loan_return: LoanReturn, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == loan_return.loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.status == LoanStatus.RETURNED:
        raise HTTPException(status_code=400, detail="Book already returned")
    
    # Update loan status
    loan.status = LoanStatus.RETURNED
    loan.return_date = datetime.utcnow()
    
    # Return book to inventory and update user borrow counts
    return_book_to_inventory(loan.book_id, db)
    decrement_user_borrows(loan.user_id, db)
    
    db.commit()
    db.refresh(loan)
    return loan

@router.get("/loans/overdue", response_model=List[OverdueLoanResponse])
def get_overdue_loans(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    loans = db.query(Loan).filter(
        Loan.status == LoanStatus.ACTIVE
    ).all()
    overdue_loans = [
        {
            "id": loan.id,
            "user": get_user_details(loan.user_id, db),
            "book": get_book_details(loan.book_id, db),
            "issue_date": loan.issue_date,
            "due_date": loan.due_date,
            "days_overdue": (loan.due_date- now).days
        }
        for loan in loans
    ]
    return overdue_loans

@router.get("/loans/{user_id}", response_model=List[LoanHistoryResponse])
def get_loan_history(user_id: int, db: Session = Depends(get_db)):
    loans = db.query(Loan).filter(Loan.user_id == user_id).all()
    # Fetch book details for each loan using helper function
    loan_histories = [
        {
            "id": loan.id,
            "book": get_book_details(loan.book_id, db),
            "issue_date": loan.issue_date,
            "due_date": loan.due_date,
            "return_date": loan.return_date,
            "status": loan.status
        }
        for loan in loans
    ]
    return loan_histories

@router.put("/loans/{id}/extend", response_model=ExtendedLoanResponse)
def extend_loan(id: int, extend: LoanExtend, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.status == LoanStatus.RETURNED:
        raise HTTPException(status_code=400, detail="Cannot extend a returned loan")
    original_due_date = loan.due_date
    loan.due_date = original_due_date + timedelta(days=extend.extension_days)
    loan.extensions_count += 1
    db.commit()
    db.refresh(loan)
    return {
        "id": loan.id,
        "user_id": loan.user_id,
        "book_id": loan.book_id,
        "issue_date": loan.issue_date,
        "original_due_date": original_due_date,
        "extended_due_date": loan.due_date,
        "status": loan.status,
        "extensions_count": loan.extensions_count
    }

def get_overdue_loans_count(db: Session) -> int:
    now = datetime.utcnow()
    return db.query(Loan).filter(Loan.status == LoanStatus.ACTIVE).count()

def get_loans_today_count(db: Session) -> int:
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return db.query(Loan).filter(Loan.issue_date >= today_start).count()

def get_returns_today_count(db: Session) -> int:
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return db.query(Loan).filter(Loan.return_date >= today_start).count()

@router.get("/stats/overview", response_model=OverviewStatsResponse)
def get_overview_stats(db: Session = Depends(get_db)):
    total_users = get_total_users(db)
    total_type_books = get_total_type_books(db)
    total_books = get_total_books(db)
    books_available = get_books_available(db)
    books_borrowed = get_books_borrowed(db)
    overdue_loans = get_overdue_loans_count(db)
    loans_today = get_loans_today_count(db)
    returns_today = get_returns_today_count(db)
    return {
        "total_type_books": total_type_books,
        "total_books": total_books,
        "total_users": total_users,
        "books_available": books_available,
        "books_borrowed": books_borrowed,
        "overdue_loans": overdue_loans,
        "loans_today": loans_today,
        "returns_today": returns_today
    }