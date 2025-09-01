from pydantic import BaseModel
from typing import Dict, Any, Optional

class UserStatusResponse(BaseModel):
    user_id: int
    is_online: bool
    last_seen: Optional[str] = None

class FriendsStatusResponse(BaseModel):
    online_status: Dict[int, bool]
    last_seen: Dict[int, Optional[str]]

class UserStatusUpdate(BaseModel):
    user_id: int
    is_online: bool

class HeartbeatRequest(BaseModel):
    msg_type: str = "heartbeat"
    timestamp: str