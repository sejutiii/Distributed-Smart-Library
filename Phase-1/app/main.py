from fastapi import FastAPI
from app.database import Base, engine
from app.routes import users, books, loans

app = FastAPI(title="Smart Library System")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(users.router)
app.include_router(books.router)
app.include_router(loans.router)