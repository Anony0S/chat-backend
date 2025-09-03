from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_current_user
from app.models.message import Message
from app.schemas.message import MessageOut, MessageSend
from typing import List

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/history", response_model=List[MessageOut])
def get_message_history(
    user_id: int = Query(..., description="对方用户id"),
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    messages = (
        db.query(Message)
        .filter(
            ((Message.from_id == current_user.id) & (Message.to_id == user_id))
            | ((Message.from_id == user_id) & (Message.to_id == current_user.id))
        )
        .order_by(Message.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return messages


@router.get("/unread", response_model=List[MessageOut])
def get_unread_messages(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    messages = (
        db.query(Message)
        .filter(Message.to_id == current_user.id, Message.is_read == False)
        .order_by(Message.created_at.asc())
        .all()
    )
    return messages


@router.post("/send", response_model=MessageOut)
def send_message(
    message_data: MessageSend,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    发送消息（支持文本、图片或混合消息）
    """
    # 验证消息内容
    if not message_data.content and not message_data.image_url:
        raise HTTPException(
            status_code=400, 
            detail="消息不能为空，至少需要文本或图片"
        )
    
    # 确定消息类型
    if message_data.content and message_data.image_url:
        message_data.msg_type = "mixed"
    elif message_data.image_url:
        message_data.msg_type = "image"
    else:
        message_data.msg_type = "text"
    
    # 创建消息
    new_message = Message(
        from_id=current_user.id,
        to_id=message_data.to_id,
        content=message_data.content,
        msg_type=message_data.msg_type,
        image_url=message_data.image_url,
        image_name=message_data.image_name
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return new_message


@router.post("/read")
def mark_messages_read(
    from_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    messages = (
        db.query(Message)
        .filter(
            Message.from_id == from_id,
            Message.to_id == current_user.id,
            Message.is_read == False,
        )
        .all()
    )
    for msg in messages:
        msg.is_read = True
    db.commit()
    return {"updated": len(messages)}
