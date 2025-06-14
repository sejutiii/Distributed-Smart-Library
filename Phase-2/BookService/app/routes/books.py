from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database import get_db
from app.models.book import Book
from app.schemas.book import BookCreate, BookResponse, BookAvailabilityUpdate, BookSearchResponse

router = APIRouter(prefix="/api/books", tags=["Books"])

@router.post("/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.isbn == book.isbn).first()
    if db_book:
        raise HTTPException(status_code=400, detail="ISBN already exists")
    new_book = Book(**book.dict(), available_copies=book.copies)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@router.get("/", response_model=BookSearchResponse)
def search_books(search: str = "", page: int = 1, per_page: int = 10, db: Session = Depends(get_db)):
    query = db.query(Book).filter(
        or_(
            Book.title.ilike(f"%{search}%"),
            Book.author.ilike(f"%{search}%"),
            Book.isbn.ilike(f"%{search}%")
        )
    )
    total = query.count()
    books = query.offset((page - 1) * per_page).limit(per_page).all()
    return {"books": books, "total": total, "page": page, "per_page": per_page}

#stats

@router.get("/stats", tags=["Books"])
def get_book_stats(db: Session = Depends(get_db)):
    total_books = db.query(Book).count()
    total_copies = db.query(func.sum(Book.copies)).scalar() or 0
    available_copies = db.query(func.sum(Book.available_copies)).scalar() or 0
    return {"books": total_books, "total_copies": total_copies, "available_copies": available_copies}

@router.get("/{id}", response_model=BookResponse)
def get_book(id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{id}", response_model=BookResponse)
def update_book(id: int, book_update: BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book_update.dict().items():
        setattr(db_book, key, value)
    db_book.available_copies = db_book.copies  # Reset available copies
    db.commit()
    db.refresh(db_book)
    return db_book

@router.patch("/{id}/availability", response_model=BookResponse)
def update_availability(id: int, update: BookAvailabilityUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if update.operation == "increment":
        book.available_copies = update.available_copies
    elif update.operation == "decrement":
        book.available_copies = update.available_copies
    else:
        raise HTTPException(status_code=400, detail="Invalid operation")
    db.commit()
    db.refresh(book)
    return book

@router.delete("/{id}", status_code=204)
def delete_book(id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return

@router.get("/{id}/availability")
def check_book_availability(id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.available_copies < 1:
        raise HTTPException(status_code=400, detail="No available copies")
    return {"id": book.id, "available_copies": book.available_copies}