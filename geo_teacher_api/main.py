from contextlib import asynccontextmanager
from .endpoints import auth, users
from .db.session import engine
from sqlmodel import SQLModel
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="Geo Teacher API", lifespan=lifespan)

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])