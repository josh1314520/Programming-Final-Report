import os
import json
import sqlite3
from flask import Blueprint, request, jsonify

# 建立災難模擬的 Blueprint，方便組長整合進 main.py
simulation_bp = Blueprint('simulation', __name__)

# 記憶體內的基礎災難模板
CRASH_TEMPLATES = {
    "2008_crash": {"stock_drop": 0.55, "recovery_months": 24, "name": "2008 年金融海嘯"},
    "covid_2020": {"stock_drop": 0.35, "recovery_months": 8, "name": "2020 年 COVID-19 閃崩"}
}

def get_db_connection():
    conn = sqlite3.connect('adventurer_vault.db')  # 確保與 init_db.py 的資料庫名稱一致
    conn.row_factory = sqlite3.Row
    return conn

@simulation_bp.route('/api/disaster_test', methods=['POST'])
def disaster_test():
    """
    情境災難壓力測試 API
    輸入 JSON 範例: {"student_id": "D1490050", "disaster_type": "2008_crash"}
    """
    data = request.json or {}
    student_id = data.get("student_id")
    disaster_type = data.get("disaster_type", "2008_crash")
   
    if not student_id:
        return jsonify({"error": "缺少學號資料"}), 400

    conn = get_db_connection()
   
    # 1. 跨模組數據聯動：撈取【陳宇睿負責的虛擬股市】中，該使用者的股市總資產
    user_asset = conn.execute(
        "SELECT SUM(stock_quantity * current_price) as total_stock FROM investments WHERE student_id = ?",
        (student_id,)
    ).fetchone()
   
    # 若該使用者目前尚未開戶或無持股，給予 100,000 元作為基本體驗金進行壓測
    total_stock_value = user_asset['total_stock'] if user_asset and user_asset['total_stock'] else 100000.0
   
    # 2. 跨模組數據聯動：撈取【吳秉洋負責的守護靈裝備】中，該使用者的保險防禦力（護甲值）
    user_armor = conn.execute(
        "SELECT insurance_armor FROM guardian WHERE student_id = ?",
        (student_id,)
    ).fetchone()
   
    # 保險防禦力設定為 0 ~ 100 之間，最高可抵免 80% 的災難資產虧損
    armor_value = user_armor['insurance_armor'] if user_armor else 0
    insurance_mitigation = min(armor_value / 100.0, 0.8)
   
    conn.close()

    # 3. API 斷網備援邏輯 (Fallback Mechanism)
    crash_info = CRASH_TEMPLATES.get(disaster_type)
    if not crash_info:
        # 當記憶體樣板異常或外部金融 API 斷網時，自動讀取本地端備援的靜態 JSON 檔案
        fallback_path = os.path.join(os.path.dirname(__file__), '2008_crash.json')
        if os.path.exists(fallback_path):
            with open(fallback_path, 'r', encoding='utf-8') as f:
                crash_info = json.load(f)
        else:
            # 最終防線：若連 JSON 都不存在，採用寫死的保底數據
            crash_info = {"stock_drop": 0.50, "recovery_months": 18, "name": "歷史金融風暴(備援數據)"}

    # 4. 風險壓力測試核心計算
    base_drop_rate = crash_info["stock_drop"]
    # 實際跌幅受到保險防禦力的保護： 實際跌幅 = 基礎跌幅 * (1 - 保險抵免率)
    actual_drop_rate = base_drop_rate * (1 - insurance_mitigation)
   
    loss_amount = total_stock_value * actual_drop_rate
    remaining_asset = total_stock_value - loss_amount

    # 5. 引導至保險系統與任務系統的 GameFi 閉環導引
    if insurance_mitigation < 0.2:
        advice = f"🚨 警告！由於您的『保險護甲值』過低（目前抵免：{insurance_mitigation*100:.0f}%），資產近乎腰斬！建議立刻前往【吳秉洋的裝備系統】配置保單提升守護靈護甲！"
    else:
        advice = f"🛡️ 防禦成功！您的『保險護甲』發揮功效（成功抵免：{insurance_mitigation*100:.0f}% 的虧損），成功幫財富森林抵擋了大部分的海嘯衝擊！"

    return jsonify({
        "status": "success",
        "student_id": student_id,
        "disaster_name": crash_info["name"],
        "original_asset": round(total_stock_value, 2),
        "loss_amount": round(loss_amount, 2),
        "remaining_asset": round(remaining_asset, 2),
        "recovery_period_months": crash_info["recovery_months"],
        "insurance_protection_rate": f"{insurance_mitigation * 100:.1f}%",
        "gamefi_advice": advice
    })
