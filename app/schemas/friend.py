from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime


class FriendRequest(BaseModel):
    friend_id: int


class FriendUserInfo(BaseModel):
    id: int
    username: str
    avatar: Optional[str] = None
    email: Optional[str] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None

    model_config = {"from_attributes": True}


class FriendBase(BaseModel):
    id: int
    user_id: int
    friend_id: int
    status: str
    created_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime) -> str:
        return created_at.isoformat()

    model_config = {"from_attributes": True}


class FriendListResponse(FriendBase):
    user: Optional[FriendUserInfo] = None


class FriendAcceptResponse(FriendBase):
    friend: Optional[FriendUserInfo] = None
