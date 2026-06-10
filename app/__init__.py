import os
from flask import Flask
from app.database import init_db

def create_app():
    """
    建立並配置 Flask 應用程式。
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'adventurers_secret_vault_key'),
    )

    # 確保 instance 資料夾存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 初始化資料庫表格與種子資料
    with app.app_context():
        init_db()

    # 註冊網頁頁面路由與 API 路由 Blueprints
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    return app
