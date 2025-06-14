from fastapi import FastAPI
from app.routes import books
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Service")
app.include_router(books.router)