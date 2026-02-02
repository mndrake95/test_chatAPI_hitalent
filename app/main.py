from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from passlib.context import CryptContext
from app.database import engine, Base, get_db
from app import schemas
from app import models

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Chat_API", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "App is running"}



# Юзеры

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

# Сообщения

@app.post("/messages/", response_model=schemas.MessageRead, status_code=201)
async def create_message(message: schemas.MessageCreate, db: AsyncSession = Depends(get_db)):
    new_message = models.Message(text=message.text, chat_id=message.chat_id, author_id=message.author_id)
    query = select(models.Chat).where(models.Chat.id == message.chat_id)
    result = await db.execute(query)
    chat_exists = result.scalar_one_or_none()
    if chat_exists is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message   