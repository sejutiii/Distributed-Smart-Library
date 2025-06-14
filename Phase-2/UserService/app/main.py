from fastapi import FastAPI
from app.routes import users
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Service")
app.include_router(users.router)