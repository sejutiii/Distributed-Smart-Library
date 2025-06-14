from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate, BookResponse, PopularBookResponse
from typing import List, Dict

router = APIRouter(prefix="/api/books", tags=["Books"])

@router.post("/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.isbn == book.isbn).first()
    if db_book:
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")
    new_book = Book(**book.dict(), available_copies=book.copies)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@router.get("/", response_model=List[BookResponse])
def search_books(search: str = "", db: Session = Depends(get_db)):
    books = db.query(Book).filter(
        (Book.title.ilike(f"%{search}%")) |
        (Book.author.ilike(f"%{search}%"))
    ).all()
    return books

@router.get("/popular", response_model=List[PopularBookResponse])
def get_popular_books(db: Session = Depends(get_db)):
    books = db.query(Book).order_by(Book.borrow_count.desc()).limit(10).all()
    return books


@router.get("/{id}", response_model=BookResponse)
def get_book(id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{id}", response_model=BookResponse)
def update_book(id: int, book_update: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    # Validate available_copies <= copies
    if book_update.available_copies > book_update.copies:
        raise HTTPException(
            status_code=400,
            detail="Available copies cannot be greater than total copies"
        )
    for key, value in book_update.dict().items():
        setattr(book, key, value)
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

# Helper functions

def get_total_type_books(db: Session) -> int:
    return db.query(Book).count()

def get_total_books(db: Session) -> int:
    return sum(book.copies for book in db.query(Book).all())

def get_books_borrowed(db: Session) -> int:
    return sum(book.copies - book.available_copies for book in db.query(Book).all())

def get_books_available(db: Session) -> int:
    total_books = get_total_books(db)
    books_borrowed = get_books_borrowed(db)
    return total_books - books_borrowed

@router.get("/{id}/availability")
def check_book_availability(id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.available_copies < 1:
        raise HTTPException(status_code=400, detail="No available copies")
    return {"id": book.id, "available_copies": book.available_copies}

def borrow_book(book_id: int, db: Session) -> None:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book.available_copies -= 1
    book.borrow_count += 1
    db.commit()

def return_book_to_inventory(book_id: int, db: Session) -> None:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book.available_copies += 1
    db.commit()

def get_book_details(book_id: int, db: Session) -> Dict:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"id": book.id, "title": book.title, "author": book.author}