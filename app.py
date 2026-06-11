import os
from app import create_app
from app.database import init_db

app = create_app()

# 如果資料庫尚未初始化，自動進行初始化
db_path = app.config['DATABASE']
if not os.path.exists(db_path):
    print("Database not found. Initializing database...")
    with app.app_context():
        init_db()

if __name__ == '__main__':
    # 啟動 Flask 開發伺服器
    app.run(debug=True, host='127.0.0.1', port=5000)
