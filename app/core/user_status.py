from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.user import User
from app.models.friend import Friend
from typing import Dict, Any
from datetime import datetime, timezone, timedelta

class UserStatusManager:
    def __init__(self, db: Session):
        self.db = db
    
    def update_user_status(self, user_id: int, is_online: bool = True):
        """更新用户在线状态"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_online = is_online
            user.last_seen = datetime.now(timezone.utc) if not is_online else None
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def get_user_status(self, user_id: int) -> Dict[str, Any]:
        """获取用户状态"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"is_online": False, "last_seen": None}
        
        return {
            "is_online": user.is_online,
            "last_seen": user.last_seen.isoformat() if user.last_seen else None
        }
    
    def get_friends_status(self, user_id: int) -> Dict[int, Dict[str, Any]]:
        """获取用户所有好友的在线状态"""
        # 获取所有好友ID
        friends = self.db.query(Friend).filter(
            and_(
                Friend.status == "accepted",
                (Friend.user_id == user_id) | (Friend.friend_id == user_id)
            )
        ).all()
        
        friend_ids = []
        for friend in friends:
            if friend.user_id == user_id:
                friend_ids.append(friend.friend_id)
            else:
                friend_ids.append(friend.user_id)
        
        # 获取好友状态
        status_dict = {}
        if friend_ids:
            friends_users = self.db.query(User).filter(User.id.in_(friend_ids)).all()
            for friend_user in friends_users:
                status_dict[friend_user.id] = {
                    "is_online": friend_user.is_online,
                    "last_seen": friend_user.last_seen.isoformat() if friend_user.last_seen else None
                }
        
        return status_dict
    
    def mark_user_offline(self, user_id: int):
        """标记用户为离线"""
        return self.update_user_status(user_id, False)
    
    def cleanup_offline_users(self, timeout_minutes: int = 5):
        """清理超时离线用户"""
        timeout_time = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
        offline_users = self.db.query(User).filter(
            and_(
                User.is_online == True,
                User.last_seen < timeout_time
            )
        ).all()
        
        for user in offline_users:
            user.is_online = False
            user.last_seen = datetime.now(timezone.utc)
        
        self.db.commit()
        return len(offline_users)