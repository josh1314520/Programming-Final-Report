import sqlite3
import os

def init_db():
    # 確保 instance 目錄存在
    os.makedirs('instance', exist_ok=True)
    db_path = os.path.join('instance', 'database.db')
    
    connection = sqlite3.connect(db_path)
    
    with open('database/schema.sql') as f:
        connection.executescript(f.read())
        
    connection.commit()
    connection.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
