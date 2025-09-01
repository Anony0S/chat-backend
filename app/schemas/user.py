from pydantic import BaseModel, EmailStr, field_serializer
from typing import Optional
from datetime import datetime

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
    is_online: Optional[bool] = None
    last_seen: Optional[datetime] = None

    @field_serializer('last_seen')
    def serialize_last_seen(self, last_seen: datetime) -> Optional[str]:
        if last_seen is None:
            return None
        return last_seen.isoformat()

    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    avatar: Optional[str] = None
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None
