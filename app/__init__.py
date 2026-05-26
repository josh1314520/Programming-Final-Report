import os
import sqlite3
from flask import Flask, g

def get_db_connection():
    """取得資料庫連線，每個 Request 共享同一個連線"""
    if 'db' not in g:
        db_path = os.path.join(g.current_instance_path, 'database.db')
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db_connection(e=None):
    """關閉資料庫連線"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    """初始化資料庫並載入 schema.sql 內建資料"""
    db_path = os.path.join(app.instance_path, 'database.db')
    
    # 確保 instance 目錄存在
    os.makedirs(app.instance_path, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    schema_path = os.path.join(app.root_path, '..', 'database', 'schema.sql')
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        print("資料庫初始化完成，成功載入 Schema 與種子資料！")
    except Exception as e:
        print(f"資料庫初始化失敗: {e}")
    finally:
        conn.close()

def create_app():
    """Flask App 工廠函數"""
    app = Flask(__name__, instance_relative_config=True)
    
    # 預設配置
    app.config.from_mapping(
        SECRET_KEY='dev-guardian-vault-secret-key-1314520',
    )
    
    # 確保 instance 資料夾存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # 設定 appcontext_processor 傳遞 instance_path
    @app.before_request
    def before_request():
        g.current_instance_path = app.instance_path

    # 註冊資料庫關閉處理
    app.teardown_appcontext(close_db_connection)
    
    # 初始化資料庫
    init_db(app)
    
    # 註冊 Blueprints
    from app.routes.main import main_bp
    from app.routes.guardian import guardian_bp
    from app.routes.equipment import equipment_bp
    from app.routes.summon import summon_bp
    from app.routes.insurance import insurance_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(guardian_bp, url_prefix='/api/guardians')
    app.register_blueprint(equipment_bp, url_prefix='/api/equipment')
    app.register_blueprint(summon_bp, url_prefix='/api/summon')
    app.register_blueprint(insurance_bp, url_prefix='/api/insurance')
    
    return app
