import os
from dotenv import load_dotenv
from app import create_app

# 載入環境變數
load_dotenv()

app = create_app()

if __name__ == '__main__':
    # 預設啟動於 5000 埠
    app.run(host='127.0.0.1', port=5000, debug=True)
