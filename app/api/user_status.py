from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_current_user
from app.core.user_status import UserStatusManager
from app.schemas.user_status import FriendsStatusResponse
from app.models.user import User
from typing import Dict, Any

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/status", response_model=Dict[str, Any])
def get_user_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户状态"""
    status_manager = UserStatusManager(db)
    return status_manager.get_user_status(current_user.id)

@router.get("/friends/status", response_model=FriendsStatusResponse)
def get_friends_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有好友的在线状态"""
    status_manager = UserStatusManager(db)
    friends_status = status_manager.get_friends_status(current_user.id)
    
    online_status = {uid: status["is_online"] for uid, status in friends_status.items()}
    last_seen = {uid: status["last_seen"] for uid, status in friends_status.items()}
    
    return FriendsStatusResponse(
        online_status=online_status,
        last_seen=last_seen
    )

@router.post("/status/heartbeat")
def update_heartbeat(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户心跳（保持在线状态）"""
    status_manager = UserStatusManager(db)
    status_manager.update_user_status(current_user.id, True)
    return {"message": "Heartbeat updated"}