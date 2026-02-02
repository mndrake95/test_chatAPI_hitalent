from pydantic import BaseModel, EmailStr, UUID4, Field
from typing import List, Optional
from datetime import datetime

# Схемы Юзеров
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: UUID4

    class Config:
        from_attributes = True

# Схемы Сообщений

class MessageBase(BaseModel):
    text: str = Field(..., max_length=5000)

class MessageCreate(MessageBase):
    chat_id: UUID4
    author_id: UUID4


class MessageRead(MessageBase):
    id: UUID4
    chat_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

# Схемы Чатов

class ChatBase(BaseModel):
    title: str = Field(..., max_length=200)

class ChatCreate(ChatBase):
    pass

class ChatRead(ChatBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True