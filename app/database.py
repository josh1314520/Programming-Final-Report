import sqlite3
import os
import json
from flask import current_app, g

DATABASE_PATH = os.path.join('instance', 'database.db')

def get_db_connection():
    """
    建立並回傳 SQLite 資料庫連線，設定 row_factory 為 Row 以利欄位名稱存取。
    """
    db_dir = os.path.dirname(DATABASE_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    初始化資料庫表結構，若表格不存在則進行建立，並寫入預設的初始金庫資源與歷史種子報告。
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. 建立金庫狀態表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vault_status (
            id INTEGER PRIMARY KEY,
            gold INTEGER NOT NULL DEFAULT 5000,
            mana_crystals INTEGER NOT NULL DEFAULT 2000,
            bonds INTEGER NOT NULL DEFAULT 2000,
            dragon_eggs INTEGER NOT NULL DEFAULT 500,
            supplies INTEGER NOT NULL DEFAULT 500
        )
    ''')

    # 2. 建立壓力測試報告表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stress_test_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            disaster_type TEXT NOT NULL,
            portfolio_distribution TEXT NOT NULL, -- JSON String
            hedging_upgrades TEXT NOT NULL,        -- JSON String
            max_drawdown REAL NOT NULL,
            recovery_period INTEGER NOT NULL,
            initial_total_val REAL NOT NULL,
            min_total_val REAL NOT NULL,
            final_total_val REAL NOT NULL,
            hedging_advice TEXT NOT NULL,
            chart_data TEXT NOT NULL               -- JSON String
        )
    ''')

    # 3. 建立股票投資組合表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL,
            stock_type TEXT NOT NULL,
            shares REAL NOT NULL,
            current_price REAL NOT NULL
        )
    ''')

    # 4. 建立守護防禦力（保險）表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guardian (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            defense_power INTEGER NOT NULL DEFAULT 0
        )
    ''')

    # 3. 檢查並寫入金庫預設初始資源
    cursor.execute('SELECT COUNT(*) FROM vault_status')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO vault_status (id, gold, mana_crystals, bonds, dragon_eggs, supplies)
            VALUES (1, 5000, 2000, 2000, 500, 500)
        ''')
        conn.commit()

    # 4. 檢查並寫入歷史種子資料，讓歷史頁面不空白，展現專業感
    cursor.execute('SELECT COUNT(*) FROM stress_test_reports')
    if cursor.fetchone()[0] == 0:
        # 種子資料 1：2008年金融海嘯測試（高波動資產受重創）
        portfolio_1 = {
            "gold": 10,
            "mana_crystals": 40,
            "bonds": 20,
            "dragon_eggs": 20,
            "supplies": 10
        }
        chart_data_1 = []
        val_1 = 10000.0
        # 模擬一個重創後緩慢復原的走勢
        for m in range(25):
            if m < 8:
                val_1 = val_1 * (1 - 0.06 - (0.01 * (8-m)))
            elif m < 15:
                val_1 = val_1 * (1 + 0.01)
            else:
                val_1 = val_1 * (1 + 0.025)
            chart_data_1.append({"month": m, "value": round(val_1, 2)})
            
        cursor.execute('''
            INSERT INTO stress_test_reports (
                disaster_type, portfolio_distribution, hedging_upgrades, 
                max_drawdown, recovery_period, initial_total_val, 
                min_total_val, final_total_val, hedging_advice, chart_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            '2008 年矮人銀行金融海嘯',
            json.dumps(portfolio_1),
            json.dumps([]),
            46.85,
            24, # 24個月尚未完全恢復
            10000.0,
            5315.0,
            6850.0,
            '您的投資組合中，「魔力水晶」與「飛龍蛋」佔比高達 60%。在此次矮人銀行信用崩潰中，高風險板塊全面失血，且因為沒有購買「公會存託保險」，導致皇家公債的部分也蒙受了無效對沖。建議大幅提升「實體黃金」以作為熊市避難所，並配置至少 20% 黃金對沖合約。',
            json.dumps(chart_data_1)
        ))

        # 種子資料 2：2020年魔力瘟疫疫情測試（配置黃金與物資，成功避險）
        portfolio_2 = {
            "gold": 40,
            "mana_crystals": 10,
            "bonds": 20,
            "dragon_eggs": 5,
            "supplies": 25
        }
        chart_data_2 = []
        val_2 = 10000.0
        # 模擬一個瘟疫爆發初期跌，但物資大漲、黃金保值快速恢復的走勢
        for m in range(25):
            if m == 0:
                val_2 = 10000.0
            elif m <= 3:
                val_2 = val_2 * 0.95  # 輕微回檔
            elif m <= 12:
                val_2 = val_2 * 1.025 # 快速回升
            else:
                val_2 = val_2 * 1.015 # 平穩
            chart_data_2.append({"month": m, "value": round(val_2, 2)})
            
        cursor.execute('''
            INSERT INTO stress_test_reports (
                disaster_type, portfolio_distribution, hedging_upgrades, 
                max_drawdown, recovery_period, initial_total_val, 
                min_total_val, final_total_val, hedging_advice, chart_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            '2020 年魔力瘟疫疫情大爆發',
            json.dumps(portfolio_2),
            json.dumps(['強化冷鏈糧倉']),
            14.26,
            7, # 7個月即恢復
            10000.0,
            8574.0,
            11850.0,
            '非常出色的防禦布局！您配置了高達 40% 的實體黃金以抵禦大盤崩盤，且在「強化冷鏈糧倉」的加持下，您的糧食儲備在第 4 個月價格飛漲時為您帶來了豐厚的利潤。這完美抵銷了魔力水晶在疫情初期的跌幅。繼續保持此類平衡防禦配置！',
            json.dumps(chart_data_2)
        ))
        conn.commit()

    # 7. 檢查並寫入預設股票與股數 (investments)
    cursor.execute('SELECT COUNT(*) FROM investments')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO investments (student_id, stock_code, stock_name, stock_type, shares, current_price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [
            ('STU12345', '2330.TW', '台積電', 'tech', 1000, 800.0),
            ('STU12345', '1301.TW', '台塑', 'traditional', 2000, 70.0),
            ('STU12345', '1760.TW', '寶齡富錦', 'healthcare', 500, 100.0),
        ])
        conn.commit()

    # 8. 檢查並寫入預設防禦力 (guardian)
    cursor.execute('SELECT COUNT(*) FROM guardian')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO guardian (student_id, defense_power)
            VALUES (?, ?)
        ''', ('STU12345', 2500))
        conn.commit()

    conn.close()
