from flask import Blueprint, render_template
from app.models.dashboard import get_adventurer

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

@dashboard_bp.route('/')
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
    
    return render_template(
        'dashboard.html', 
        adventurer=adventurer,
        rating_info=rating_info,
        tree_stage=tree_stage
    )
