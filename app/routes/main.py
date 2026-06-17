from flask import Blueprint, render_template
from app.models.vault import get_vault_status

main_bp = Blueprint('main', __name__)

@main_bp.route('/simulator')
def index():
    """
    渲染冒險者金庫首頁：包含當前物資狀態、投資比例拉桿、災難選擇面板與動態水晶球終端。
    """
    vault = get_vault_status()
    return render_template('simulator.html', vault=vault)

@main_bp.route('/reports')
def reports():
    """
    渲染歷史壓力測試編年史頁面。
    """
    return render_template('reports.html')
