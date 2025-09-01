"""
数据库初始化脚本：解决迁移问题
"""
import sqlite3
import os

def init_database():
    """初始化数据库，确保表结构正确"""
    db_path = "app.db"
    
    # 如果数据库存在，先删除
    if os.path.exists(db_path):
        os.remove(db_path)
        print("删除旧数据库文件")
    
    # 创建新数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR UNIQUE NOT NULL,
            hashed_password VARCHAR NOT NULL,
            avatar VARCHAR,
            email VARCHAR UNIQUE,
            nickname VARCHAR,
            gender VARCHAR,
            is_online BOOLEAN DEFAULT FALSE,
            last_seen DATETIME
        )
    """)
    print("创建 users 表")
    
    # 创建好友表
    cursor.execute("""
        CREATE TABLE friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            friend_id INTEGER NOT NULL,
            status VARCHAR DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (friend_id) REFERENCES users (id)
        )
    """)
    print("创建 friends 表")
    
    # 创建消息表
    cursor.execute("""
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_id INTEGER NOT NULL,
            to_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            msg_type VARCHAR DEFAULT 'text',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (from_id) REFERENCES users (id),
            FOREIGN KEY (to_id) REFERENCES users (id)
        )
    """)
    print("创建 messages 表")
    
    conn.commit()
    conn.close()
    print("数据库初始化完成")

if __name__ == "__main__":
    init_database()