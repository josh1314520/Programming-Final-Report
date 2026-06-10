import sqlite3
import os
from datetime import datetime
from .evolution import calculate_guardian_form

def get_db_connection():
    # 這裡的寫法假設執行路徑在專案根目錄
    db_path = os.path.join(os.getcwd(), 'instance', 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_guardian(user_id: int):
    """取得用戶的守護靈資料"""
    try:
        conn = get_db_connection()
        guardian = conn.execute('SELECT * FROM guardians WHERE user_id = ?', (user_id,)).fetchone()
        conn.close()
        
        if guardian:
            return dict(guardian)
        return None
    except Exception as e:
        print(f"Error fetching guardian: {e}")
        return None

def update_guardian_status(user_id: int, asset_value: float, risk_tolerance: str):
    """更新用戶資產與風險偏好，並觸發演化計算寫入資料庫"""
    try:
        # 計算新的演化型態與顏色
        form = calculate_guardian_form(asset_value, risk_tolerance)
        new_stage = form['stage']
        new_color = form['color']
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = get_db_connection()
        
        # 檢查用戶是否存在，若不存在則新增，否則更新
        existing = conn.execute('SELECT id FROM guardians WHERE user_id = ?', (user_id,)).fetchone()
        
        if existing:
            conn.execute('''
                UPDATE guardians 
                SET asset_value = ?, risk_tolerance = ?, stage = ?, color = ?, updated_at = ?
                WHERE user_id = ?
            ''', (asset_value, risk_tolerance, new_stage, new_color, now, user_id))
        else:
            conn.execute('''
                INSERT INTO guardians (user_id, asset_value, risk_tolerance, stage, color, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, asset_value, risk_tolerance, new_stage, new_color, now))
            
        conn.commit()
        conn.close()
        
        # 回傳最新的資料
        return get_guardian(user_id)
        
    except Exception as e:
        print(f"Error updating guardian: {e}")
        return None
