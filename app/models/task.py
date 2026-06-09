import sqlite3
from flask import current_app

def get_db_connection():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def check_news_read(adventurer_id, news_url):
    """檢查該名使用者是否已經閱讀過這則新聞（今天內，或不限時間皆可，這裡我們先不限時間）"""
    try:
        conn = get_db_connection()
        record = conn.execute(
            "SELECT 1 FROM daily_tasks WHERE adventurer_id = ? AND task_type = 'read_news' AND reference_id = ?",
            (adventurer_id, news_url)
        ).fetchone()
        conn.close()
        return bool(record)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def record_news_task(adventurer_id, news_url, reward_amount=50):
    """記錄新聞閱讀任務，並給予對應獎勵點數"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. 記錄完成的任務
        cursor.execute(
            "INSERT INTO daily_tasks (adventurer_id, task_type, reference_id, reward_amount) VALUES (?, ?, ?, ?)",
            (adventurer_id, 'read_news', news_url, reward_amount)
        )
        
        # 2. 增加使用者的 total_assets
        cursor.execute(
            "UPDATE adventurers SET total_assets = total_assets + ? WHERE id = ?",
            (reward_amount, adventurer_id)
        )
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False
