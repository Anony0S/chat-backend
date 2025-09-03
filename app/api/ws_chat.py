from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.security import get_current_user
from app.core.database import SessionLocal
from app.core.user_status import UserStatusManager
from app.models.message import Message
from app.models.user import User
from app.models.friend import Friend
from sqlalchemy.orm import Session
from typing import Dict, Set
from datetime import datetime, timezone
import json
import asyncio

router = APIRouter()

active_connections: Dict[int, WebSocket] = {}
heartbeat_tasks: Dict[int, asyncio.Task] = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def notify_friends_status_change(user_id: int, is_online: bool, db: Session):
    """通知好友用户状态变更"""
    # 获取所有好友
    friends = db.query(Friend).filter(
        (Friend.user_id == user_id) | (Friend.friend_id == user_id),
        Friend.status == "accepted"
    ).all()
    
    friend_ids = []
    for friend in friends:
        friend_ids.append(friend.friend_id if friend.user_id == user_id else friend.user_id)
    
    # 通知在线好友
    status_message = {
        "msg_type": "user_status",
        "user_id": user_id,
        "status": "online" if is_online else "offline",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    for friend_id in friend_ids:
        friend_ws = active_connections.get(friend_id)
        if friend_ws:
            try:
                await friend_ws.send_text(json.dumps(status_message))
            except:
                pass

async def heartbeat_handler(websocket: WebSocket, user_id: int, db: Session):
    """心跳处理器"""
    
    while True:
        try:
            # 发送心跳检查
            await asyncio.sleep(30)  # 每30秒检查一次
            
            # 检查连接是否仍然活跃
            if user_id not in active_connections:
                break
                
            # 发送心跳响应
            await websocket.send_text(json.dumps({
                "msg_type": "heartbeat_response",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
            
        except WebSocketDisconnect:
            break
        except Exception as e:
            print(f"Heartbeat error for user {user_id}: {e}")
            break

@router.websocket("/ws/chat/{token}")
async def websocket_chat(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    # 简单 token 校验，生产建议用 get_current_user 依赖
    from jose import jwt, JWTError
    from app.core.security import SECRET_KEY, ALGORITHM
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user = db.query(User).filter(User.username == user_id).first()
        if not user:
            await websocket.close()
            return
    except JWTError:
        await websocket.close()
        return
    
    await websocket.accept()
    active_connections[user.id] = websocket
    
    # 用户上线，更新状态并通知好友
    status_manager = UserStatusManager(db)
    status_manager.update_user_status(user.id, True)
    await notify_friends_status_change(user.id, True, db)
    
    # 启动心跳任务
    heartbeat_task = asyncio.create_task(heartbeat_handler(websocket, user.id, db))
    heartbeat_tasks[user.id] = heartbeat_task
    
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            msg_type = msg.get("msg_type", "text")
            
            if msg_type == "heartbeat":
                # 更新用户在线状态
                status_manager.update_user_status(user.id, True)
                continue  # 心跳消息处理完成
            
            if msg_type == "read":
                # 已读回执处理
                from_id = msg.get("from_id")  # 谁发的消息
                message_ids = msg.get("message_ids", [])
                # 批量标记为已读
                updated = 0
                if message_ids:
                    messages = db.query(Message).filter(
                        Message.id.in_(message_ids),
                        Message.from_id == from_id,
                        Message.to_id == user.id,
                        Message.is_read == False
                    ).all()
                    for m in messages:
                        m.is_read = True
                    db.commit()
                    updated = len(messages)
                # 推送回执给原发送方
                from_ws = active_connections.get(from_id)
                if from_ws:
                    await from_ws.send_text(json.dumps({
                        "msg_type": "read_receipt",
                        "from_id": user.id,  # 已读方
                        "to_id": from_id,    # 原发送方
                        "message_ids": message_ids,
                        "updated": updated
                    }))
                continue
                
            # 普通消息处理
            to_id = msg.get("to_id")
            content = msg.get("content")
            image_url = msg.get("image_url")
            image_name = msg.get("image_name")
            
            # 存储消息
            message = Message(
                from_id=user.id,
                to_id=to_id,
                content=content,
                msg_type=msg_type,
                image_url=image_url,
                image_name=image_name,
                created_at=datetime.utcnow(),
                is_read=False
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            # 推送给目标用户
            to_ws = active_connections.get(to_id)
            if to_ws:
                await to_ws.send_text(json.dumps({
                    "from_id": user.id,
                    "to_id": to_id,
                    "content": content,
                    "msg_type": msg_type,
                    "image_url": image_url,
                    "image_name": image_name,
                    "created_at": message.created_at.isoformat(),
                    "id": message.id
                }))
                
    except WebSocketDisconnect:
        # 用户下线，更新状态并通知好友
        active_connections.pop(user.id, None)
        heartbeat_tasks.pop(user.id, None)
        status_manager.update_user_status(user.id, False)
        await notify_friends_status_change(user.id, False, db)
        
        # 取消心跳任务
        if user.id in heartbeat_tasks:
            heartbeat_tasks[user.id].cancel()
            del heartbeat_tasks[user.id]
