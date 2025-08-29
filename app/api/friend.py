from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.database import SessionLocal
from app.core.security import get_current_user
from app.models.friend import Friend
from app.models.user import User
from app.schemas.friend import (
    FriendAcceptResponse,
    FriendBase,
    FriendListResponse,
    FriendRequest,
)
from typing import List

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/add", response_model=FriendBase)
def add_friend(
    request: FriendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if request.friend_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as friend")
    # 检查是否已存在好友关系
    exist = (
        db.query(Friend)
        .filter(
            (
                (Friend.user_id == current_user.id)
                & (Friend.friend_id == request.friend_id)
            )
            | (
                (Friend.user_id == request.friend_id)
                & (Friend.friend_id == current_user.id)
            )
        )
        .first()
    )
    if exist:
        raise HTTPException(
            status_code=400,
            detail="Friend request already exists or you are already friends",
        )
    # 检查目标用户是否存在
    target = db.query(User).filter(User.id == request.friend_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found")
    friend = Friend(
        user_id=current_user.id, friend_id=request.friend_id, status="pending"
    )
    db.add(friend)
    db.commit()
    db.refresh(friend)
    return friend


@router.get("/list", response_model=List[FriendAcceptResponse])
def list_friends(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    friends = (
        db.query(Friend)
        .options(joinedload(Friend.friend))
        .filter((Friend.user_id == current_user.id) & (Friend.status == "accepted"))
        .all()
    )
    return friends


@router.get("/requests", response_model=List[FriendListResponse])
def list_friend_requests(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    requests = (
        db.query(Friend)
        .options(joinedload(Friend.user))
        .filter(Friend.friend_id == current_user.id, Friend.status == "pending")
        .all()
    )
    return requests


@router.post("/accept/{request_id}", response_model=FriendAcceptResponse)
def accept_friend(
    request_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    friend = (
        db.query(Friend)
        .filter(
            Friend.id == request_id,
            Friend.friend_id == current_user.id,
            Friend.status == "pending",
        )
        .first()
    )
    friend.status = "accepted"
    reverse_exist = (
        db.query(Friend)
        .filter(Friend.user_id == current_user.id, Friend.friend_id == friend.user_id)
        .first()
    )
    if not reverse_exist:
        reverse_friend = Friend(
            user_id=current_user.id, friend_id=friend.user_id, status="accepted"
        )
        db.add(reverse_friend)
    db.commit()
    db.refresh(friend)
    return friend


@router.post("/reject/{request_id}", response_model=FriendBase)
def reject_friend(
    request_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    friend = (
        db.query(Friend)
        .filter(
            Friend.id == request_id,
            Friend.friend_id == current_user.id,
            Friend.status == "pending",
        )
        .first()
    )
    if not friend:
        raise HTTPException(status_code=404, detail="Friend request not found")
    friend.status = "rejected"
    db.commit()
    db.refresh(friend)
    return friend
