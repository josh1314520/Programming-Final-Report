import sqlite3
import os

def init_db():
    # 確保 instance 目錄存在
    os.makedirs('instance', exist_ok=True)
    db_path = os.path.join('instance', 'database.db')
    
    # 建立與 SQLite 的連線
    connection = sqlite3.connect(db_path)
    
    # 啟用外鍵約束
    connection.execute("PRAGMA foreign_keys = ON;")
    
    # 讀取並執行 schema.sql 腳本
    # schema.sql 位於本檔案同級目錄下的 schema.sql，或者上一層的 database 目錄
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if not os.path.exists(schema_path):
        schema_path = os.path.join('database', 'schema.sql')
        
    print(f"Reading schema from: {schema_path}")
    with open(schema_path, encoding='utf-8') as f:
        connection.executescript(f.read())
        
    # 儲存並關閉連線
    connection.commit()
    connection.close()
    
    print("資料庫與 Schema 初始化成功！所有模組資料表與初始資料已載入。")

if __name__ == '__main__':
    init_db()
