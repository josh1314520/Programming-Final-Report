def calculate_guardian_form(asset_value: float, risk_tolerance: str) -> dict:
    """
    根據資產與風險偏好計算守護靈的型態(stage)與顏色(color)。
    
    外觀型態階段 (stage) 由「資產數量 (asset_value)」決定：
    - < 10,000 ➞ Stage 1 (幼年期)
    - 10,000 ~ 49,999 ➞ Stage 2 (成長期)
    - >= 50,000 ➞ Stage 3 (完全體)

    顏色 (color) 由「風險偏好 (risk_tolerance)」決定：
    - conservative (保守) ➞ 藍色 (Blue)
    - balanced (穩健) ➞ 綠色 (Green)
    - aggressive (積極) ➞ 紅色 (Red)
    """
    
    # 決定 Stage
    if asset_value < 10000:
        stage = 1
    elif asset_value < 50000:
        stage = 2
    else:
        stage = 3
        
    # 決定 Color
    color_map = {
        'conservative': 'Blue',
        'balanced': 'Green',
        'aggressive': 'Red'
    }
    
    # 若輸入不在預設範圍內，預設給予綠色
    color = color_map.get(risk_tolerance.lower(), 'Green')
    
    return {
        'stage': stage,
        'color': color
    }
