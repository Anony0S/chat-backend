from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import Base
from app.models.friend import Friend  # 确保表被创建
from app.models.message import Message  # 新增消息表

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建表
Base.metadata.create_all(bind=engine)

# 依赖注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
