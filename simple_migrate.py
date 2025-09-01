import sqlite3

# 连接到数据库
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

try:
    # 检查是否已经有is_online列
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'is_online' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN is_online BOOLEAN DEFAULT 0")
        print("成功添加 is_online 列")
    else:
        print("is_online 列已存在")
    
    if 'last_seen' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN last_seen DATETIME")
        print("成功添加 last_seen 列")
    else:
        print("last_seen 列已存在")
    
    # 验证列是否添加成功
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    print(f"当前列: {columns}")
    
except Exception as e:
    print(f"迁移失败: {e}")
finally:
    conn.commit()
    conn.close()
    print("迁移完成")