from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_current_user
from app.models.message import Message
from app.schemas.message import MessageOut
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
