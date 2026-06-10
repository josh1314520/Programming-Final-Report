import sqlite3
import os

def init_db():
    # 確保 instance 目錄存在
    os.makedirs('instance', exist_ok=True)
    db_path = os.path.join('instance', 'database.db')
    
    # 建立與 SQLite 的連線
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # 啟用外鍵約束
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. 建立 users (用戶) 資料表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        student_id TEXT PRIMARY KEY,
        gold INTEGER DEFAULT 0,
        exp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1
    );
    """)
    
    # 2. 建立 guardian (守護靈) 資料表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS guardian (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        stage INTEGER DEFAULT 1,
        color TEXT DEFAULT 'Green',
        defense INTEGER DEFAULT 0,
        FOREIGN KEY (student_id) REFERENCES users (student_id) ON DELETE CASCADE
    );
    """)
    
    # 3. 建立 tasks (任務) 資料表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        main_status TEXT DEFAULT 'pending',
        news_completed_at DATETIME,
        FOREIGN KEY (student_id) REFERENCES users (student_id) ON DELETE CASCADE
    );
    """)
    
    # 4. 建立 investments (投資) 資料表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        stock_code TEXT NOT NULL,
        shares_held INTEGER DEFAULT 0,
        average_cost REAL DEFAULT 0.0,
        FOREIGN KEY (student_id) REFERENCES users (student_id) ON DELETE CASCADE
    );
    """)
    
    # 儲存並關閉連線
    connection.commit()
    connection.close()
    
    print("資料庫與 Schema 初始化成功！外鍵關聯已建立。")

if __name__ == '__main__':
    init_db()
