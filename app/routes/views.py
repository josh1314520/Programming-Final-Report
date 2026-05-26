from flask import Blueprint, render_template

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    """
    渲染冒險者金庫主線任務系統的單頁儀表板。
    """
    return render_template('index.html')
