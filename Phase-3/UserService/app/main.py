from fastapi import FastAPI
from app.routes import users
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
            title="User Service",
            root_path="/api/users"
            )
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the User Service!"}