from flask import Blueprint, request, jsonify
from app.models.insurance import InsuranceArmorModel

insurance_bp = Blueprint('insurance_api', __name__)

@insurance_bp.route('/analyze', methods=['POST'])
def analyze_policy():
    """保單分析並轉換為守護靈防禦力 API"""
    data = request.get_json() or {}
    
    guardian_id = data.get('guardian_id')
    life = data.get('life_coverage', 0)
    medical = data.get('medical_coverage', 0)
    accident = data.get('accident_coverage', 0)
    
    if not guardian_id:
        return jsonify({"success": False, "message": "未提供守護靈 ID！"}), 400
        
    try:
        # 限制極端輸入
        life = max(0, int(life))
        medical = max(0, int(medical))
        accident = max(0, int(accident))
    except ValueError:
        return jsonify({"success": False, "message": "保額輸入必須是數字！"}), 400
        
    success, result = InsuranceArmorModel.analyze_and_save(guardian_id, life, medical, accident)
    
    if success:
        return jsonify({"success": True, "data": result})
    else:
        return jsonify({"success": False, "message": result}), 400
