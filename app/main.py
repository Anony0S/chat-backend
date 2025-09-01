from fastapi import FastAPI
from .api import auth, user, friend, ws_chat, message, user_status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 允许跨域请求
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(friend.router, prefix="/api/friend", tags=["friend"])
app.include_router(ws_chat.router, prefix="/api", tags=["ws_chat"])
app.include_router(message.router, prefix="/api/message", tags=["message"])
app.include_router(user_status.router, prefix="/api/user", tags=["user_status"])
