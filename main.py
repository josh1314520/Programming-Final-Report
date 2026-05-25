from flask import Flask

def create_app():
    # 建立 Flask 應用程式實例
    app = Flask(__name__)
    
    # 基本設定 (可依據實際需求替換為 config.py)
    app.config['SECRET_KEY'] = 'your_secret_key_here'

    # ==========================================
    # Flask Blueprints 註冊區
    # ==========================================
    # 做法：請每位組員在 app/routes/ 目錄下建立自己的 .py 檔案
    # 並在自己的檔案中宣告 Blueprint，最後統一在這裡註冊。
    # 這樣大家同時開發不同功能時，就不會發生 main.py 的嚴重衝突！
    
    # 1. 守護靈模組 (由 A 同學負責)
    # from app.routes.guardian import guardian_bp
    # app.register_blueprint(guardian_bp, url_prefix='/guardian')

    # 2. 任務模組 (由 B 同學負責)
    # from app.routes.tasks import tasks_bp
    # app.register_blueprint(tasks_bp, url_prefix='/tasks')

    # 3. 投資模組 (由 C 同學負責)
    # from app.routes.investments import investments_bp
    # app.register_blueprint(investments_bp, url_prefix='/investments')

    # ==========================================
    # 全域通用路由 (首頁等)
    # ==========================================
    @app.route('/')
    def index():
        # 在這裡可以 render_template('index.html')
        return "歡迎來到冒險者金庫！"

    return app

if __name__ == '__main__':
    # 啟動伺服器
    app = create_app()
    app.run(debug=True)
