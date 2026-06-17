import sqlite3
import json
from app.database import get_db_connection

def create_report(disaster_type, portfolio_distribution, hedging_upgrades, 
                  max_drawdown, recovery_period, initial_total_val, 
                  min_total_val, final_total_val, hedging_advice, chart_data):
    """
    新增一筆壓力測試報告，並回傳該筆報告的自動遞增 ID。
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 轉換 list/dict 為 JSON 字串
        portfolio_str = json.dumps(portfolio_distribution)
        upgrades_str = json.dumps(hedging_upgrades)
        chart_str = json.dumps(chart_data)
        
        cursor.execute('''
            INSERT INTO stress_test_reports (
                disaster_type, portfolio_distribution, hedging_upgrades, 
                max_drawdown, recovery_period, initial_total_val, 
                min_total_val, final_total_val, hedging_advice, chart_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            disaster_type, portfolio_str, upgrades_str,
            max_drawdown, recovery_period, initial_total_val,
            min_total_val, final_total_val, hedging_advice, chart_str
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error creating stress test report: {e}")
        conn.rollback()
        return None

def get_all_reports():
    """
    獲取所有歷史壓力測試報告，依測試時間降序排列。
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stress_test_reports ORDER BY tested_at DESC")
        rows = cursor.fetchall()
        reports = []
        for r in rows:
            report_dict = dict(r)
            # 解析 JSON 欄位以利前端方便直接使用
            report_dict['portfolio_distribution'] = json.loads(report_dict['portfolio_distribution'])
            report_dict['hedging_upgrades'] = json.loads(report_dict['hedging_upgrades'])
            report_dict['chart_data'] = json.loads(report_dict['chart_data'])
            reports.append(report_dict)
        return reports
    except sqlite3.Error as e:
        print(f"Error fetching all reports: {e}")
        return []

def get_report_by_id(report_id):
    """
    依 ID 取得單筆詳細歷史壓力測試報告。
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stress_test_reports WHERE id = ?", (report_id,))
        row = cursor.fetchone()
        if row:
            report_dict = dict(row)
            report_dict['portfolio_distribution'] = json.loads(report_dict['portfolio_distribution'])
            report_dict['hedging_upgrades'] = json.loads(report_dict['hedging_upgrades'])
            report_dict['chart_data'] = json.loads(report_dict['chart_data'])
            return report_dict
        return None
    except sqlite3.Error as e:
        print(f"Error fetching report {report_id}: {e}")
        return None
