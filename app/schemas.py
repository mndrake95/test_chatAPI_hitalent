from pydantic import BaseModel, EmailStr, UUID4

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: UUID4

    class Config:
        from_attributes = True
