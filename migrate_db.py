"""
数据库迁移脚本：添加用户在线状态字段
"""
import sqlite3
import os

def migrate_database():
    """迁移数据库，添加用户在线状态相关字段"""
    db_path = "app.db"
    
    if not os.path.exists(db_path):
        print("数据库文件不存在，将自动创建")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 添加 is_online 列
    try:
        cursor.execute("""
            ALTER TABLE users ADD COLUMN is_online BOOLEAN DEFAULT FALSE
        """)
        print("成功添加 is_online 列")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("is_online 列已存在")
        else:
            print(f"添加 is_online 列失败: {e}")
    
    # 添加 last_seen 列
    try:
        cursor.execute("""
            ALTER TABLE users ADD COLUMN last_seen DATETIME
        """)
        print("成功添加 last_seen 列")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("last_seen 列已存在")
        else:
            print(f"添加 last_seen 列失败: {e}")
    
    conn.commit()
    conn.close()
    print("数据库迁移完成")

if __name__ == "__main__":
    migrate_database()