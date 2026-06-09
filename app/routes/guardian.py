from flask import Blueprint, request, jsonify
from app.models.guardian import get_guardian, update_guardian_status

guardian_bp = Blueprint('guardian', __name__)

@guardian_bp.route('/status', methods=['GET'])
def get_status():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({"status": "error", "message": "Missing user_id parameter"}), 400
        
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid user_id format"}), 400
        
    guardian = get_guardian(user_id)
    
    if not guardian:
        return jsonify({"status": "error", "message": "Guardian not found for this user"}), 404
        
    response_data = {
        "status": "success",
        "data": {
            "user_id": guardian['user_id'],
            "asset_value": guardian['asset_value'],
            "risk_tolerance": guardian['risk_tolerance'],
            "guardian_form": {
                "stage": guardian['stage'],
                "color": guardian['color']
            }
        }
    }
    
    return jsonify(response_data), 200

@guardian_bp.route('/update', methods=['POST'])
def update_status():
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON payload"}), 400
        
    user_id = data.get('user_id')
    asset_value = data.get('asset_value')
    risk_tolerance = data.get('risk_tolerance')
    
    if user_id is None or asset_value is None or risk_tolerance is None:
        return jsonify({"status": "error", "message": "Missing required fields: user_id, asset_value, risk_tolerance"}), 400
        
    try:
        user_id = int(user_id)
        asset_value = float(asset_value)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid data format for user_id or asset_value"}), 400
        
    updated_guardian = update_guardian_status(user_id, asset_value, risk_tolerance)
    
    if not updated_guardian:
        return jsonify({"status": "error", "message": "Failed to update guardian status"}), 500
        
    response_data = {
        "status": "success",
        "data": {
            "user_id": updated_guardian['user_id'],
            "asset_value": updated_guardian['asset_value'],
            "risk_tolerance": updated_guardian['risk_tolerance'],
            "guardian_form": {
                "stage": updated_guardian['stage'],
                "color": updated_guardian['color']
            }
        }
    }
    
    return jsonify(response_data), 200
