"""
数据库迁移脚本：添加消息图片字段
"""
import sqlite3
import os

def migrate_database():
    """迁移数据库，添加消息图片相关字段"""
    db_path = "app.db"
    
    if not os.path.exists(db_path):
        print("数据库文件不存在，将自动创建")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. 修改 content 列允许为空（图片消息可能没有文本）
    try:
        # SQLite 不支持直接修改列的 nullable 属性，需要重新创建表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_id INTEGER NOT NULL,
                to_id INTEGER NOT NULL,
                content TEXT,
                msg_type TEXT DEFAULT 'text',
                image_url TEXT,
                image_name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (from_id) REFERENCES users (id),
                FOREIGN KEY (to_id) REFERENCES users (id)
            )
        """)
        print("创建新表结构成功")
        
        # 复制现有数据
        cursor.execute("""
            INSERT INTO messages_new (
                id, from_id, to_id, content, msg_type, 
                created_at, is_read
            )
            SELECT 
                id, from_id, to_id, content, msg_type, 
                created_at, is_read
            FROM messages
        """)
        print("数据复制成功")
        
        # 删除旧表
        cursor.execute("DROP TABLE messages")
        print("删除旧表成功")
        
        # 重命名新表
        cursor.execute("ALTER TABLE messages_new RENAME TO messages")
        print("表重命名成功")
        
    except sqlite3.OperationalError as e:
        print(f"迁移失败: {e}")
        conn.rollback()
        return
    
    conn.commit()
    conn.close()
    print("数据库迁移完成")

if __name__ == "__main__":
    migrate_database()