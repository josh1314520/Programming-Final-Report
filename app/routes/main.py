from flask import Blueprint, render_template, jsonify, request
from app.models.player import PlayerModel
from app.models.guardian import GuardianModel
from app.models.equipment import EquipmentModel

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    """首頁儀表板"""
    player = PlayerModel.get_player()
    guardians = GuardianModel.get_all()
    equipments = EquipmentModel.get_all()
    
    # 計算一些統計數據
    total_power = sum(g['power'] for g in guardians)
    guardian_count = len(guardians)
    equipment_count = len(equipments)
    
    return render_template(
        'dashboard.html',
        player=player,
        guardians=guardians[:3], # 首頁只展示最強的 3 位
        total_power=total_power,
        guardian_count=guardian_count,
        equipment_count=equipment_count
    )

@main_bp.route('/guardians')
def guardian_hall():
    """守護靈殿堂頁面"""
    player = PlayerModel.get_player()
    guardians = GuardianModel.get_all()
    
    # 取得未裝備的各部位裝備，供穿戴選單使用
    unequipped_weapons = EquipmentModel.get_all(type_filter='weapon', unequipped_only=True)
    unequipped_armors = EquipmentModel.get_all(type_filter='armor', unequipped_only=True)
    unequipped_accessories = EquipmentModel.get_all(type_filter='accessory', unequipped_only=True)
    
    return render_template(
        'guardians.html',
        player=player,
        guardians=guardians,
        unequipped_weapons=unequipped_weapons,
        unequipped_armors=unequipped_armors,
        unequipped_accessories=unequipped_accessories
    )

@main_bp.route('/equipment')
def equipment_vault():
    """裝備庫頁面"""
    player = PlayerModel.get_player()
    equipments = EquipmentModel.get_all()
    
    return render_template(
        'equipment.html',
        player=player,
        equipments=equipments
    )

@main_bp.route('/summon')
def summon_altar():
    """召喚祭壇頁面"""
    player = PlayerModel.get_player()
    return render_template('summon.html', player=player)

@main_bp.route('/api/player/daily', methods=['POST'])
def get_daily_supply():
    """領取每日補給 API"""
    success, result = PlayerModel.claim_daily()
    if success:
        return jsonify({"success": True, "data": result})
    else:
        return jsonify({"success": False, "message": result}), 400

@main_bp.route('/api/player/status', methods=['GET'])
def get_player_status():
    """獲取玩家最新資源狀態與總戰力 API"""
    player = PlayerModel.get_player()
    guardians = GuardianModel.get_all()
    total_power = sum(g['power'] for g in guardians)
    
    return jsonify({
        "success": True,
        "gold": player['gold'],
        "soul_stones": player['soul_stones'],
        "total_power": total_power
    })
