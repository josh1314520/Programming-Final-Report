import sqlite3
from app import get_db_connection

class InsuranceArmorModel:
    @staticmethod
    def get_by_guardian_id(guardian_id):
        """取得守護靈的保險護甲資料"""
        db = get_db_connection()
        row = db.execute(
            "SELECT * FROM insurance_armor WHERE guardian_id = ?",
            (guardian_id,)
        ).fetchone()
        
        if row:
            return dict(row)
        else:
            # 回傳預設未分析狀態
            return {
                "guardian_id": guardian_id,
                "life_coverage": 0,
                "medical_coverage": 0,
                "accident_coverage": 0,
                "armor_level": 0,
                "defense_value": 0,
                "armor_name": "無護具"
            }

    @staticmethod
    def get_armor_name(level):
        """根據護具等級決定護具稱號"""
        if level <= 0:
            return "無護具"
        elif level <= 2:
            return "木質布衣"
        elif level <= 5:
            return "黑鐵輕甲"
        elif level <= 10:
            return "白銀聖盾"
        elif level <= 15:
            return "黃金神域聖衣"
        else:
            return "鑽石不滅神裝"

    @staticmethod
    def analyze_and_save(guardian_id, life_coverage, medical_coverage, accident_coverage):
        """將壽險、醫療險、意外險額度轉化為防禦力並更新資料庫"""
        db = get_db_connection()
        
        # 1. 取得舊數值供升級動畫比對
        old_armor = InsuranceArmorModel.get_by_guardian_id(guardian_id)
        old_defense = old_armor.get("defense_value", 0)
        
        # 2. 計算防禦力與護具等級
        # 壽險：每 100 萬 +1 等級，+50 防禦
        life_level = life_coverage // 100
        life_def = life_level * 50
        
        # 醫療險：每 1000 元 +1 等級，+30 防禦
        medical_level = medical_coverage // 1000
        medical_def = medical_level * 30
        
        # 意外險：每 100 萬 +20 防禦 (但不增加主要護甲等級)
        accident_level = accident_coverage // 100
        accident_def = accident_level * 20
        
        # 護甲等級為壽險等級與醫療險等級加總，低消 1 級 (若有保額)
        raw_level = life_level + medical_level
        armor_level = max(1, raw_level) if (life_coverage > 0 or medical_coverage > 0 or accident_coverage > 0) else 0
        
        defense_value = life_def + medical_def + accident_def
        armor_name = InsuranceArmorModel.get_armor_name(armor_level)
        
        try:
            # 3. 寫入資料庫 (INSERT OR REPLACE 確保只有一筆紀錄)
            db.execute(
                """INSERT OR REPLACE INTO insurance_armor 
                   (guardian_id, life_coverage, medical_coverage, accident_coverage, armor_level, defense_value, armor_name) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (guardian_id, life_coverage, medical_coverage, accident_coverage, armor_level, defense_value, armor_name)
            )
            db.commit()
            
            # 4. 取得最新的守護靈資訊供計算戰力與回傳
            from app.models.guardian import GuardianModel
            updated_g = GuardianModel.get_by_id(guardian_id)
            
            return True, {
                "guardian_id": guardian_id,
                "guardian_name": updated_g["name"],
                "life_coverage": life_coverage,
                "medical_coverage": medical_coverage,
                "accident_coverage": accident_coverage,
                "armor_level": armor_level,
                "defense_value": defense_value,
                "armor_name": armor_name,
                "old_defense_value": old_defense,
                "defense_increased": max(0, defense_value - old_defense),
                "total_defense": updated_g["total_def"],
                "new_power": updated_g["power"]
            }
        except Exception as e:
            db.rollback()
            return False, f"儲存保險護甲數值失敗: {str(e)}"
