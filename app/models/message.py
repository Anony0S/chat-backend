from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import timezone
from app.models.user import Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    from_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=True)  # 允许为空，图片消息可能没有文本
    msg_type = Column(String, default="text")  # text, image, mixed
    image_url = Column(String, nullable=True)  # 图片存储路径
    image_name = Column(String, nullable=True)  # 原始文件名
    created_at = Column(DateTime, default=timezone.utc)
    is_read = Column(Boolean, default=False)
    sender = relationship("User", foreign_keys=[from_id])
    receiver = relationship("User", foreign_keys=[to_id])
