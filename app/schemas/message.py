from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime

class MessageSend(BaseModel):
    to_id: int
    content: Optional[str] = None
    msg_type: Optional[str] = "text"
    image_url: Optional[str] = None
    image_name: Optional[str] = None

class MessageOut(BaseModel):
    id: int
    from_id: int
    to_id: int
    content: Optional[str] = None
    msg_type: str
    image_url: Optional[str] = None
    image_name: Optional[str] = None
    created_at: datetime
    is_read: bool

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime) -> str:
        return created_at.isoformat()

    model_config = {"from_attributes": True}
