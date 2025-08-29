from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    avatar: Optional[str] = None
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    avatar: Optional[str] = None
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None

    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    avatar: Optional[str] = None
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None
