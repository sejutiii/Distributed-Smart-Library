from fastapi import FastAPI
from app.routes import loans
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Loan Service", 
              root_path="/api/loans")
app.include_router(loans.router)