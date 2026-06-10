import sqlite3
from app.database import get_db_connection

def get_vault_status():
    """
    獲取目前金庫中所有資產的數量。
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vault_status WHERE id = 1")
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except sqlite3.Error as e:
        print(f"Error fetching vault status: {e}")
        return None
    finally:
        conn.close()

def update_vault_status(gold, mana_crystals, bonds, dragon_eggs, supplies):
    """
    更新金庫中的各項資產數量。
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE vault_status 
            SET gold = ?, mana_crystals = ?, bonds = ?, dragon_eggs = ?, supplies = ?
            WHERE id = 1
        ''', (gold, mana_crystals, bonds, dragon_eggs, supplies))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error updating vault status: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def reset_vault_status():
    """
    將金庫的所有物資一鍵恢復至全滿初始狀態：
    金幣 5,000 / 魔力水晶 2,000 / 皇家公債 2,000 / 飛龍蛋 500 / 糧食儲備 500。
    """
    return update_vault_status(5000, 2000, 2000, 500, 500)
