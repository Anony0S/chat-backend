from pydantic import BaseModel
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

    model_config = {"from_attributes": True}
