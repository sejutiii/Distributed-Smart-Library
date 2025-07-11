from fastapi import FastAPI
from app.routes import loans
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Loan Service")
app.include_router(loans.router)