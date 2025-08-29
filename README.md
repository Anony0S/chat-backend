# Chat Backend

FastAPI chat application backend with user registration, login, friend management and real-time chat.

## Features

- User registration and login (JWT authentication)
- User management and profile updates
- Friend system (add, delete, list)
- Real-time chat (WebSocket)
- Message history management

## Tech Stack

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database
- **WebSocket** - Real-time communication
- **JWT** - Authentication
- **bcrypt** - Password hashing

## Project Structure

```
app/
├── api/          # API routes
│   ├── auth.py   # Authentication
│   ├── user.py   # User management
│   ├── friend.py # Friend management
│   ├── message.py# Message management
│   └── ws_chat.py# WebSocket chat
├── core/         # Core configuration
│   ├── database.py
│   └── security.py
├── models/       # Data models
│   ├── user.py
│   ├── friend.py
│   └── message.py
├── schemas/      # Pydantic schemas
│   ├── user.py
│   ├── friend.py
│   ├── message.py
│   └── token.py
└── utils/        # Utility functions
```

## Installation and Running

### Requirements

- Python 3.12+
- uv (Python package manager)

### Install Dependencies

```bash
uv sync
```

### Run Application

```bash
uvicorn app.main:app --reload
```

Application will start at http://localhost:8000

### API Documentation

After starting, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### User Management
- `GET /api/user/me` - Get current user info
- `PUT /api/user/me` - Update user info

### Friend Management
- `GET /api/friend/` - Get friend list
- `POST /api/friend/add` - Add friend
- `DELETE /api/friend/{friend_id}` - Delete friend

### Messages
- `GET /api/message/{friend_id}` - Get chat history with friend

### WebSocket
- `WS /api/ws/{user_id}` - WebSocket connection for real-time chat

## Development Notes

This project uses SQLite as the development database, database file is `app.db`.

CORS is configured to allow all origins, recommend changing to specific frontend domain for production.