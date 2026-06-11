import sqlite3

def init_mock():
    conn = sqlite3.connect('adventurer_vault.db')
    cursor = conn.cursor()
   
    # 建立模擬的股市持股表（陳宇睿負責）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investments (
            student_id TEXT,
            stock_quantity REAL,
            current_price REAL
        )
    ''')
   
    # 建立模擬的守護靈裝備表（吳秉洋負責）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guardian (
            student_id TEXT,
            insurance_armor REAL
        )
    ''')
   
    # 寫入高叡廷個人的測試數據 (學號已更換為 D1490050)
    cursor.execute("DELETE FROM investments WHERE student_id = 'D1490050'")
    cursor.execute("DELETE FROM guardian WHERE student_id = 'D1490050'")
   
    # 模擬叡廷買了 10 股、每股 1500 元的台積電 (總值 15,000)
    cursor.execute("INSERT INTO investments VALUES ('D1490050', 10, 1500)")
    # 模擬叡廷配置了保險，護甲值高達 75 分
    cursor.execute("INSERT INTO guardian VALUES ('D1490050', 75)")
   
    conn.commit()
    conn.close()
    print("測試 Mock 資料寫入成功！")

if __name__ == '__main__':
    init_mock()
