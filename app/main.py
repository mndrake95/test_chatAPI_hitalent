from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from passlib.context import CryptContext
from app.database import engine, Base, get_db
from app import schemas
from app import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Chat_API", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "App is running"}

@app.post("/users/", response_model=schemas.UserRead)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    hashed_pw = pwd_context.hash(user.password)
    new_user = models.User(username = user.username, 
                           email = user.email,
                           hashed_password = hashed_pw)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# Чаты

@app.post("/chats/", response_model=schemas.ChatRead, status_code=201)
async def create_chat(chat: schemas.ChatCreate, db: AsyncSession = Depends(get_db)):
    new_chat = models.Chat(title=chat.title)
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)
    return new_chat