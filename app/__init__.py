import os
from flask import Flask
from app.database import close_db_connection, init_db

def create_app(test_config=None):
    """
    建立並配置 Flask 應用程式。
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # 預設配置
    app.config.from_mapping(
        SECRET_KEY='adventurer_vault_secret_key',
        DATABASE=os.path.join(app.instance_path, 'database.db'),
    )

    if test_config is None:
        # 如果存在 config.py 則載入
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 載入傳入的測試配置
        app.config.from_mapping(test_config)

    # 確保 instance 目錄存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 註冊資料庫關閉鉤子
    app.teardown_appcontext(close_db_connection)

    # 註冊 Blueprint 路由
    from app.routes.views import views_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)

    return app
