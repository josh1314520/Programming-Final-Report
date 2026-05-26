from flask import Blueprint, request, jsonify
from app.models.guardian import GuardianModel

guardian_bp = Blueprint('guardian_api', __name__)

@guardian_bp.route('/<int:guardian_id>/feed', methods=['POST'])
def feed_guardian(guardian_id):
    """餵食守護靈 API"""
    success, result = GuardianModel.feed(guardian_id)
    if success:
        return jsonify({"success": True, "data": result})
    else:
        return jsonify({"success": False, "message": result}), 400

@guardian_bp.route('/<int:guardian_id>/equip', methods=['POST'])
def equip_item(guardian_id):
    """為守護靈裝備道具 API"""
    data = request.get_json() or {}
    equipment_id = data.get('equipment_id')
    
    if not equipment_id:
        return jsonify({"success": False, "message": "未提供裝備 ID！"}), 400
        
    success, result = GuardianModel.equip_item(guardian_id, equipment_id)
    if success:
        return jsonify({"success": True, "data": result})
    else:
        return jsonify({"success": False, "message": result}), 400

@guardian_bp.route('/<int:guardian_id>/unequip', methods=['POST'])
def unequip_item(guardian_id):
    """卸下守護靈身上的裝備 API"""
    data = request.get_json() or {}
    equipment_id = data.get('equipment_id')
    
    if not equipment_id:
        return jsonify({"success": False, "message": "未提供裝備 ID！"}), 400
        
    success, result = GuardianModel.unequip_item(guardian_id, equipment_id)
    if success:
        return jsonify({"success": True, "data": result})
    else:
        return jsonify({"success": False, "message": result}), 400

@guardian_bp.route('/<int:guardian_id>/delete', methods=['POST'])
def delete_guardian(guardian_id):
    """遣散守護靈 API"""
    success = GuardianModel.delete(guardian_id)
    if success:
        return jsonify({"success": True, "message": "成功將守護靈放歸虛空星海！"})
    else:
        return jsonify({"success": False, "message": "遣散守護靈失敗！"}), 500
