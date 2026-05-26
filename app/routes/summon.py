import random
from flask import Blueprint, request, jsonify
from app.models.player import PlayerModel
from app.models.guardian import GuardianModel
from app.models.equipment import EquipmentModel

summon_bp = Blueprint('summon_api', __name__)

# 守護靈召喚池
GUARDIAN_POOL = [
    {"name": "熾天神凰", "element": "Fire", "hp": 480, "atk": 90, "def": 35},
    {"name": "赤羽火靈", "element": "Fire", "hp": 400, "atk": 75, "def": 30},
    {"name": "滄海冰龍", "element": "Water", "hp": 650, "atk": 65, "def": 55},
    {"name": "浪潮歌姬", "element": "Water", "hp": 520, "atk": 50, "def": 45},
    {"name": "迅捷雷狼", "element": "Wind", "hp": 390, "atk": 92, "def": 32},
    {"name": "翡翠妖精", "element": "Wind", "hp": 430, "atk": 60, "def": 40},
    {"name": "晶岩巨人", "element": "Earth", "hp": 850, "atk": 38, "def": 85},
    {"name": "鐵甲犀牛", "element": "Earth", "hp": 720, "atk": 45, "def": 70},
    {"name": "輝光天使", "element": "Light", "hp": 550, "atk": 80, "def": 50},
    {"name": "聖光獨角獸", "element": "Light", "hp": 580, "atk": 70, "def": 55},
    {"name": "虛空獵手", "element": "Shadow", "hp": 410, "atk": 98, "def": 28},
    {"name": "暗影死神", "element": "Shadow", "hp": 460, "atk": 88, "def": 38}
]

# 裝備召喚池
EQUIPMENT_POOL = [
    # 武器 (weapon)
    {"name": "天罰雷霆之弓", "type": "weapon", "rarity": "Legendary", "hp": 0, "atk": 70, "def": 0},
    {"name": "熔岩法杖", "type": "weapon", "rarity": "Epic", "hp": 50, "atk": 35, "def": 0},
    {"name": "夜影匕首", "type": "weapon", "rarity": "Epic", "hp": 0, "atk": 40, "def": 0},
    {"name": "破鋼雙刃", "type": "weapon", "rarity": "Rare", "hp": 0, "atk": 25, "def": 0},
    {"name": "學徒木杖", "type": "weapon", "rarity": "Common", "hp": 10, "atk": 8, "def": 0},
    
    # 防具 (armor)
    {"name": "神聖天啟重鎧", "type": "armor", "rarity": "Legendary", "hp": 450, "atk": 0, "def": 50},
    {"name": "狂戰士皮甲", "type": "armor", "rarity": "Rare", "hp": 150, "atk": 10, "def": 15},
    {"name": "布製法袍", "type": "armor", "rarity": "Common", "hp": 50, "atk": 0, "def": 5},
    
    # 飾品 (accessory)
    {"name": "命運之眼星印", "type": "accessory", "rarity": "Legendary", "hp": 200, "atk": 20, "def": 15},
    {"name": "守護石戒", "type": "accessory", "rarity": "Common", "hp": 40, "atk": 0, "def": 4}
]

@summon_bp.route('', methods=['POST'])
def draw_summon():
    """進行召喚 API (1抽 或 10抽)"""
    data = request.get_json() or {}
    times = data.get('times', 1)
    
    if times not in (1, 10):
        return jsonify({"success": False, "message": "無效的召喚次數！"}), 400
        
    # 計算花費：1抽 3靈石，10抽特惠 25靈石
    cost = 3 if times == 1 else 25
    
    success, res = PlayerModel.update_resources(0, -cost)
    if not success:
        return jsonify({"success": False, "message": f"靈石不足！召喚需要 {cost} 顆靈石。"}), 400
        
    draw_results = []
    
    for _ in range(times):
        # 30% 機率抽中守護靈，70% 抽中裝備
        if random.random() < 0.30:
            # 抽守護靈
            tpl = random.choice(GUARDIAN_POOL)
            # 隨機數值微幅浮動 (-10% 到 +10%)
            var = random.uniform(0.9, 1.1)
            base_hp = int(tpl["hp"] * var)
            base_atk = int(tpl["atk"] * var)
            base_def = int(tpl["def"] * var)
            
            guardian_id = GuardianModel.create(
                name=tpl["name"],
                element=tpl["element"],
                level=1,
                xp=0,
                base_hp=base_hp,
                base_atk=base_atk,
                base_def=base_def
            )
            
            draw_results.append({
                "id": guardian_id,
                "type": "guardian",
                "name": tpl["name"],
                "element": tpl["element"],
                "level": 1,
                "base_hp": base_hp,
                "base_atk": base_atk,
                "base_def": base_def,
                "rarity": "Legendary" if tpl["name"] in ("熾天神凰", "滄海冰龍", "輝光天使") else "Epic"
            })
        else:
            # 抽裝備
            tpl = random.choice(EQUIPMENT_POOL)
            # 隨機數值微幅浮動
            var = random.uniform(0.95, 1.15)
            hp_b = int(tpl["hp"] * var) if tpl["hp"] > 0 else 0
            atk_b = int(tpl["atk"] * var) if tpl["atk"] > 0 else 0
            def_b = int(tpl["def"] * var) if tpl["def"] > 0 else 0
            
            equip_id = EquipmentModel.create(
                name=tpl["name"],
                type=tpl["type"],
                rarity=tpl["rarity"],
                level=1,
                hp_bonus=hp_b,
                atk_bonus=atk_b,
                def_bonus=def_b
            )
            
            draw_results.append({
                "id": equip_id,
                "type": "equipment",
                "equipment_type": tpl["type"],
                "name": tpl["name"],
                "rarity": tpl["rarity"],
                "level": 1,
                "hp_bonus": hp_b,
                "atk_bonus": atk_b,
                "def_bonus": def_b
            })
            
    return jsonify({
        "success": True,
        "results": draw_results,
        "soul_stones_left": res["soul_stones"],
        "gold_left": res["gold"],
        "cost_stones": cost
    })
