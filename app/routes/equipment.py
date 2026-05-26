from flask import Blueprint, request, jsonify
from app.models.equipment import EquipmentModel
from app.models.player import PlayerModel

equipment_bp = Blueprint('equipment_api', __name__)

@equipment_bp.route('/<int:equipment_id>/upgrade', methods=['POST'])
def upgrade_equipment(equipment_id):
    """強化裝備 API"""
    success, result = EquipmentModel.upgrade(equipment_id)
    if success:
        return jsonify({"success": True, "data": result})
    else:
        return jsonify({"success": False, "message": result}), 400

@equipment_bp.route('/<int:equipment_id>/sell', methods=['POST'])
def sell_equipment(equipment_id):
    """出售裝備 API"""
    equip = EquipmentModel.get_by_id(equipment_id)
    if not equip:
        return jsonify({"success": False, "message": "裝備不存在！"}), 404
        
    if equip['guardian_id'] is not None:
        return jsonify({"success": False, "message": "裝備正被守護靈穿戴中，無法出售！"}), 400
        
    # 計算出售價格
    rarity_base_gold = {
        'Common': 300,
        'Rare': 1000,
        'Epic': 3000,
        'Legendary': 8000
    }
    base = rarity_base_gold.get(equip['rarity'], 300)
    extra = (equip['level'] - 1) * 200
    total_refund = base + extra
    
    # 刪除裝備
    if EquipmentModel.delete(equipment_id):
        # 增加金幣
        PlayerModel.update_resources(total_refund, 0)
        return jsonify({
            "success": True, 
            "data": {
                "equipment_id": equipment_id,
                "name": equip['name'],
                "gold_earned": total_refund,
                "message": f"成功以 {total_refund} 金幣出售了 {equip['name']}！"
            }
        })
    else:
        return jsonify({"success": False, "message": "出售裝備失敗！"}), 500
