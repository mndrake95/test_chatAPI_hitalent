import uuid
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from passlib.context import CryptContext
from app.database import engine, Base, get_db
from typing import List
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

@app.delete("/chats/{chat_id}", status_code=204)
async def delete_chat(chat_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    query = select(models.Chat).where(models.Chat.id == chat_id)
    result = await db.execute(query)
    chat_exists = result.scalar_one_or_none()
    if chat_exists is None:
        raise HTTPException(status_code=404, detail=f"Chat with id {chat_id} not found")
    await db.delete(chat_exists)
    await db.commit()
    return None

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

@app.get("/chats/{chat_id}/messages", response_model=List[schemas.MessageRead], status_code=200)
async def get_messages_by_chat_id(chat_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    query = select(models.Message).where(models.Message.chat_id == chat_id)
    result = await db.execute(query)
    messages = result.scalars().all()
    chat_result = await db.execute(select(models.Chat).where(models.Chat.id == chat_id))
    if chat_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Chat not found")    
    return messages

@app.patch("/messages/{message_id}", response_model=schemas.MessageRead, status_code=200)
async def patch_message_by_message_id(message_id: uuid.UUID, message_update: schemas.MessageUpdate, db: AsyncSession = Depends(get_db)):
    query = select(models.Message).where(models.Message.id == message_id)
    result = await db.execute(query)
    message_obj = result.scalar_one_or_none()
    if message_obj is None:
        raise HTTPException(status_code=404, detail="Message not found")  
    message_obj.text = message_update.text
    await db.commit()
    return message_obj
