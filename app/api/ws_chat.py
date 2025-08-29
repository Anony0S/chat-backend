from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.security import get_current_user
from app.core.database import SessionLocal
from app.models.message import Message
from app.models.user import User
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime
import json

router = APIRouter()

active_connections: Dict[int, WebSocket] = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            msg_type = msg.get("msg_type", "text")
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
            # 存储消息
            message = Message(
                from_id=user.id,
                to_id=to_id,
                content=content,
                msg_type=msg_type,
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
                    "created_at": message.created_at.isoformat(),
                    "id": message.id
                }))
    except WebSocketDisconnect:
        active_connections.pop(user.id, None)
