import sqlite3
from app import get_db_connection
from app.models.player import PlayerModel

class GuardianModel:
    @staticmethod
    def create(name, element, level=1, xp=0, base_hp=100, base_atk=10, base_def=5):
        """新增一個守護靈"""
        db = get_db_connection()
        try:
            cursor = db.execute(
                """INSERT INTO guardians 
                   (name, element, level, xp, base_hp, base_atk, base_def) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, element, level, xp, base_hp, base_atk, base_def)
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def get_by_id(guardian_id):
        """取得單一守護靈資訊，包含其裝備與加成後總屬性"""
        db = get_db_connection()
        row = db.execute("SELECT * FROM guardians WHERE id = ?", (guardian_id,)).fetchone()
        if not row:
            return None
            
        guardian = dict(row)
        
        # 查詢已裝備的道具
        equip_rows = db.execute(
            "SELECT * FROM equipment WHERE guardian_id = ?",
            (guardian_id,)
        ).fetchall()
        
        equipment = {
            "weapon": None,
            "armor": None,
            "accessory": None
        }
        
        bonus_hp = 0
        bonus_atk = 0
        bonus_def = 0
        
        for er in equip_rows:
            eq = dict(er)
            eq_type = eq['type']
            if eq_type in equipment:
                equipment[eq_type] = eq
                bonus_hp += eq['hp_bonus']
                bonus_atk += eq['atk_bonus']
                bonus_def += eq['def_bonus']
                
        guardian['equipment'] = equipment
        
        # 計算總屬性
        guardian['total_hp'] = guardian['base_hp'] + bonus_hp
        guardian['total_atk'] = guardian['base_atk'] + bonus_atk
        guardian['total_def'] = guardian['base_def'] + bonus_def
        
        # 計算總戰力 (Power)
        guardian['power'] = int(
            guardian['total_hp'] * 0.2 + 
            guardian['total_atk'] * 2.0 + 
            guardian['total_def'] * 1.5
        )
        
        # 升級所需經驗值
        guardian['max_xp'] = guardian['level'] * 100
        
        return guardian

    @staticmethod
    def get_all():
        """取得所有守護靈列表，包含其詳細屬性與戰力"""
        db = get_db_connection()
        rows = db.execute("SELECT id FROM guardians ORDER BY level DESC, id ASC").fetchall()
        
        guardians = []
        for r in rows:
            g = GuardianModel.get_by_id(r['id'])
            if g:
                guardians.append(g)
        return guardians

    @staticmethod
    def delete(guardian_id):
        """刪除守護靈，並自動將其裝備卸下 (將 equipment.guardian_id 設為 NULL)"""
        db = get_db_connection()
        try:
            # 1. 卸下裝備
            db.execute("UPDATE equipment SET guardian_id = NULL WHERE guardian_id = ?", (guardian_id,))
            # 2. 刪除守護靈
            db.execute("DELETE FROM guardians WHERE id = ?", (guardian_id,))
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False

    @staticmethod
    def get_feed_cost(level):
        """計算餵食所需的金幣"""
        return level * 150

    @staticmethod
    def feed(guardian_id):
        """餵食守護靈，消耗金幣，增加經驗值並處理升級與屬性增長"""
        db = get_db_connection()
        guardian = GuardianModel.get_by_id(guardian_id)
        if not guardian:
            return False, "守護靈不存在！"
            
        cost = GuardianModel.get_feed_cost(guardian['level'])
        
        # 扣除金幣
        success, res = PlayerModel.update_resources(-cost, 0)
        if not success:
            return False, f"金幣不足！需要 {cost} 金幣。"
            
        xp_gain = 40 # 每次固定增加 40 經驗值
        new_xp = guardian['xp'] + xp_gain
        new_level = guardian['level']
        max_xp = guardian['level'] * 100
        
        is_level_up = False
        new_base_hp = guardian['base_hp']
        new_base_atk = guardian['base_atk']
        new_base_def = guardian['base_def']
        
        # 處理連續升級可能性 (雖然 40 經驗一般一次升不了一級，但也防範特殊設定)
        while new_xp >= max_xp:
            new_xp -= max_xp
            new_level += 1
            is_level_up = True
            
            # 升級屬性成長：生命+12%, 攻擊+10%, 防禦+10%
            hp_growth = int(new_base_hp * 0.12)
            atk_growth = int(new_base_atk * 0.10)
            def_growth = int(new_base_def * 0.10)
            
            # 保障最低成長值
            new_base_hp += max(hp_growth, 30)
            new_base_atk += max(atk_growth, 5)
            new_base_def += max(def_growth, 3)
            
            max_xp = new_level * 100
            
        try:
            db.execute(
                """UPDATE guardians 
                   SET level = ?, xp = ?, base_hp = ?, base_atk = ?, base_def = ? 
                   WHERE id = ?""",
                (new_level, new_xp, new_base_hp, new_base_atk, new_base_def, guardian_id)
            )
            db.commit()
            
            # 重新獲取最新資訊以回傳
            updated_guardian = GuardianModel.get_by_id(guardian_id)
            
            return True, {
                "guardian_id": guardian_id,
                "name": guardian['name'],
                "gold_spent": cost,
                "xp_gained": xp_gain,
                "old_level": guardian['level'],
                "new_level": new_level,
                "is_level_up": is_level_up,
                "new_xp": new_xp,
                "max_xp": max_xp,
                "base_hp": new_base_hp,
                "base_atk": new_base_atk,
                "base_def": new_base_def,
                "total_hp": updated_guardian['total_hp'],
                "total_atk": updated_guardian['total_atk'],
                "total_def": updated_guardian['total_def'],
                "power": updated_guardian['power']
            }
        except Exception as e:
            db.rollback()
            return False, f"餵食資料庫更新失敗: {str(e)}"

    @staticmethod
    def equip_item(guardian_id, equipment_id):
        """將裝備穿在守護靈身上的對應槽位，若該槽位已有裝備則自動先將其卸下"""
        db = get_db_connection()
        
        # 1. 取得裝備資訊與守護靈資訊
        from app.models.equipment import EquipmentModel
        equip = EquipmentModel.get_by_id(equipment_id)
        guardian = GuardianModel.get_by_id(guardian_id)
        
        if not equip or not guardian:
            return False, "裝備或守護靈不存在！"
            
        # 2. 檢查此裝備是否已被其他人裝備
        if equip['guardian_id'] is not None and equip['guardian_id'] != guardian_id:
            # 先幫別人卸下
            EquipmentModel.unequip(equipment_id)
            
        # 3. 檢查守護靈該部位目前是否有裝備，如果有，則先卸下該裝備
        current_eq_in_slot = guardian['equipment'].get(equip['type'])
        if current_eq_in_slot:
            EquipmentModel.unequip(current_eq_in_slot['id'])
            
        # 4. 穿上新裝備
        success = EquipmentModel.equip(equipment_id, guardian_id)
        if success:
            # 重新計算最新戰力
            updated_g = GuardianModel.get_by_id(guardian_id)
            return True, {
                "message": f"成功為 {guardian['name']} 裝備了 {equip['name']}！",
                "guardian": updated_g
            }
        else:
            return False, "穿上裝備失敗！"

    @staticmethod
    def unequip_item(guardian_id, equipment_id):
        """從守護靈身上卸下指定裝備"""
        db = get_db_connection()
        from app.models.equipment import EquipmentModel
        equip = EquipmentModel.get_by_id(equipment_id)
        
        if not equip:
            return False, "裝備不存在！"
            
        if equip['guardian_id'] != guardian_id:
            return False, "該裝備並非穿戴於此守護靈！"
            
        success = EquipmentModel.unequip(equipment_id)
        if success:
            updated_g = GuardianModel.get_by_id(guardian_id)
            return True, {
                "message": f"成功卸下 {equip['name']}！",
                "guardian": updated_g
            }
        else:
            return False, "卸下裝備失敗！"
