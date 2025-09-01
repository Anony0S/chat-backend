from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime

class MessageSend(BaseModel):
    to_id: int
    content: str
    msg_type: Optional[str] = "text"

class MessageOut(BaseModel):
    id: int
    from_id: int
    to_id: int
    content: str
    msg_type: str
    created_at: datetime
    is_read: bool

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime) -> str:
        return created_at.isoformat()

    model_config = {"from_attributes": True}
