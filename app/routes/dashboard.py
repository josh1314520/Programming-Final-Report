import math
import sqlite3
from flask import Blueprint, render_template, jsonify, request, current_app
from app.models.dashboard import get_adventurer
from app.models.guardian import get_guardian, update_guardian_status

dashboard_bp = Blueprint('dashboard', __name__)

def calculate_rating(assets):
    tiers = [
        {"name": "銅牌勇者", "threshold": 0, "next_threshold": 10000},
        {"name": "銀牌勇者", "threshold": 10000, "next_threshold": 50000},
        {"name": "金牌勇者", "threshold": 50000, "next_threshold": 100000},
        {"name": "鑽石勇者", "threshold": 100000, "next_threshold": None}
    ]
    
    current_tier = tiers[0]
    for tier in tiers:
        if assets >= tier["threshold"]:
            current_tier = tier
        else:
            break
            
    if current_tier["next_threshold"]:
        progress = (assets - current_tier["threshold"]) / (current_tier["next_threshold"] - current_tier["threshold"]) * 100
        needed_assets = current_tier["next_threshold"] - assets
    else:
        progress = 100
        needed_assets = 0
        
    return {
        "tier_name": current_tier["name"],
        "progress": round(progress, 2),
        "needed_assets": needed_assets,
        "next_threshold": current_tier["next_threshold"]
    }

@dashboard_bp.route('/dashboard')
def dashboard():
    # Assume user ID 1 is logged in
    adventurer = get_adventurer(1)
    
    if not adventurer:
        return "無法找到勇者資料", 404
        
    assets = adventurer['total_assets']
    
    rating_info = calculate_rating(assets)
    
    # 決定樹木的生長階段 (1-4)
    if assets < 10000:
        tree_stage = 1
    elif assets < 50000:
        tree_stage = 2
    elif assets < 100000:
        tree_stage = 3
    else:
        tree_stage = 4
        
    # 獲取或更新守護靈狀態以連動總資產
    guardian = get_guardian(1)
    if not guardian:
        guardian = update_guardian_status(1, assets, 'balanced')
    else:
        guardian = update_guardian_status(1, assets, guardian['risk_tolerance'])

    # 獲取安全防禦度 (防禦力)
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT insurance_score FROM guardian WHERE student_id = '1'")
    g_data = cursor.fetchone()
    security_score = g_data['insurance_score'] if g_data else 50
    conn.close()
    
    return render_template(
        'dashboard.html', 
        adventurer=adventurer,
        rating_info=rating_info,
        tree_stage=tree_stage,
        guardian=guardian,
        security_score=security_score
    )

def get_db_connection():
    try:
        db_path = current_app.config['DATABASE']
    except RuntimeError:
        db_path = 'adventure_vault.db'
        
    import os
    if not os.path.exists(db_path) and os.path.exists('adventure_vault.db'):
        db_path = 'adventure_vault.db'
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@dashboard_bp.route('/api/hero_status', methods=['GET'])
def get_hero_status():
    student_id = request.args.get('student_id')
    if not student_id:
        return jsonify({"error": "Missing student_id"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. 撈取宇睿的虛擬股市總資產 (代表攻擊力)
    cursor.execute("SELECT SUM(stock_value + cash) as total_assets FROM investments WHERE student_id = ?", (student_id,))
    asset_data = cursor.fetchone()
    total_assets = asset_data['total_assets'] if asset_data['total_assets'] else 10000.0
    
    # 2. 撈取秉洋的保險保障度 (代表護甲/防禦力)
    cursor.execute("SELECT insurance_score FROM guardian WHERE student_id = ?", (student_id,))
    guardian_data = cursor.fetchone()
    insurance_score = guardian_data['insurance_score'] if guardian_data else 50
    
    conn.close()
    
    # 3. 核心演算法：結合攻擊與防禦，並使用對數函數(Log)平滑化，避免數值通膨
    # 英雄綜合評分公式
    hero_score = (math.log10(total_assets) * 40) + (insurance_score * 0.6)
    
    # 根據綜合評分給予評級 (Rank)
    if hero_score >= 250:
        rank = "SSS 財富守護神"
    elif hero_score >= 200:
        rank = "SS 傳奇冒險家"
    elif hero_score >= 150:
        rank = "S 聖騎士"
    elif hero_score >= 100:
        rank = "A 菁英戰士"
    else:
        rank = "B 初階新手"
        
    # 計算進度條百分比 (滿分以 300 為基準)
    progress_percentage = min(100, round((hero_score / 300) * 100, 1))
    
    return jsonify({
        "student_id": student_id,
        "attack_power": round(total_assets, 2),
        "defense_power": insurance_score,
        "hero_score": round(hero_score, 2),
        "rank": rank,
        "progress_bar": progress_percentage
    })

