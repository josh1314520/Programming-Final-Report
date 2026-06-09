import math

def calculate_guardian_form(asset_value: float, risk_tolerance: str) -> dict:
    """
    根據資產與風險偏好計算守護靈的型態(stage 1~5)與顏色(Hex Color)。
    
    導入對數公式 (math.log10) 防止數值通膨：
    score = math.log10(max(asset_value, 1))
    
    外觀型態階段 (stage)：
    - Stage 1 (幼年體): score < 4 (資產 < 1萬)
    - Stage 2 (成長體): 4 <= score < 5 (資產 1萬 ~ 10萬)
    - Stage 3 (成熟體): 5 <= score < 6 (資產 10萬 ~ 100萬)
    - Stage 4 (完全體): 6 <= score < 7 (資產 100萬 ~ 1000萬)
    - Stage 5 (究極體): score >= 7 (資產 >= 1000萬)

    顏色 (color) 由「風險偏好 (risk_tolerance)」決定：
    - conservative (保守) ➞ #4A90E2
    - balanced (穩健) ➞ #50E3C2
    - aggressive (積極) ➞ #E02020
    """
    # 確保資產不小於 1，避免 Math Domain Error
    safe_asset = max(asset_value, 1)
    score = math.log10(safe_asset)
    
    # 決定 Stage
    if score < 4:
        stage = 1
    elif score < 5:
        stage = 2
    elif score < 6:
        stage = 3
    elif score < 7:
        stage = 4
    else:
        stage = 5
        
    # 決定 Color (Hex Code)
    color_map = {
        'conservative': '#4A90E2',
        'balanced': '#50E3C2',
        'aggressive': '#E02020'
    }
    
    # 若輸入不在預設範圍內，預設給予穩健綠色
    color = color_map.get(risk_tolerance.lower(), '#50E3C2')
    
    return {
        'stage': stage,
        'color': color
    }
