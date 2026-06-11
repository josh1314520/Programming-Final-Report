import os
import sqlite3
from flask import g, current_app

def get_db_connection():
    """
    取得 SQLite 資料庫連線。
    使用 Flask 的 g 物件確保在同一次 Request 中只重複使用同一個連線。
    啟用外鍵約束，並設定 Row Factory 以方便用欄位名稱取值。
    """
    if 'db' not in g:
        db_path = current_app.config['DATABASE']
        # 確保 instance 資料夾存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        # 啟用 SQLite 外鍵約束
        g.db.execute("PRAGMA foreign_keys = ON;")
        
    return g.db

def close_db_connection(e=None):
    """
    關閉目前 Request 的資料庫連線。
    會在 Flask 請求生命週期結束 (teardown_appcontext) 時自動呼叫。
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """
    初始化資料庫。
    讀取 database/schema.sql 並在 SQLite 資料庫中建立資料表與預設資料。
    """
    db_path = current_app.config['DATABASE']
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    # 尋找 schema.sql
    # 預設路徑是在專案根目錄的 database 目錄下
    schema_path = os.path.join(current_app.root_path, '..', 'database', 'schema.sql')
    if not os.path.exists(schema_path):
        # 備用路徑，如果是在 app 同級目錄
        schema_path = os.path.join(current_app.root_path, 'database', 'schema.sql')
        
    with open(schema_path, encoding='utf-8') as f:
        conn.executescript(f.read())
        
    conn.commit()
    conn.close()
    print("Database initialized successfully with default quests!")
