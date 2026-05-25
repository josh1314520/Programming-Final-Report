import os
import sqlite3
import json
from main import create_app
from database.init_db import init_db

def run_tests():
    # 1. 初始化資料庫
    print("Initializing Database...")
    init_db()
    print("Database Initialized.")

    # 2. 建立 Flask 測試客戶端
    app = create_app()
    app.testing = True
    client = app.test_client()

    print("\n--- 測試開始 ---")

    # 測試 A: 更新用戶狀態 (首次新增)
    print("\n[測試 A] 更新用戶狀態 (保守型, 資產 5000)")
    response = client.post('/api/guardian/update', json={
        "user_id": 1,
        "asset_value": 5000,
        "risk_tolerance": "conservative"
    })
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.get_json(), ensure_ascii=False, indent=2)}")

    # 測試 B: 取得用戶狀態
    print("\n[測試 B] 取得用戶狀態 (user_id = 1)")
    response = client.get('/api/guardian/status?user_id=1')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.get_json(), ensure_ascii=False, indent=2)}")

    # 測試 C: 演化測試 (資產增加，改為積極型)
    print("\n[測試 C] 更新用戶狀態 (積極型, 資產 60000)")
    response = client.post('/api/guardian/update', json={
        "user_id": 1,
        "asset_value": 60000,
        "risk_tolerance": "aggressive"
    })
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.get_json(), ensure_ascii=False, indent=2)}")
    
    # 測試 D: 千萬資產測試 (對數壓制)
    print("\n[測試 D] 更新用戶狀態 (穩健型, 資產 15000000)")
    response = client.post('/api/guardian/update', json={
        "user_id": 1,
        "asset_value": 15000000,
        "risk_tolerance": "balanced"
    })
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.get_json(), ensure_ascii=False, indent=2)}")
    
    print("\n--- 測試結束 ---")

if __name__ == '__main__':
    run_tests()
