import sqlite3
from app import get_db_connection
from app.models.player import PlayerModel

class EquipmentModel:
    @staticmethod
    def create(name, type, rarity, level=1, hp_bonus=0, atk_bonus=0, def_bonus=0, guardian_id=None):
        """新增一件裝備"""
        db = get_db_connection()
        try:
            cursor = db.execute(
                """INSERT INTO equipment 
                   (name, type, rarity, level, hp_bonus, atk_bonus, def_bonus, guardian_id) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, type, rarity, level, hp_bonus, atk_bonus, def_bonus, guardian_id)
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def get_by_id(equipment_id):
        """取得單一裝備"""
        db = get_db_connection()
        row = db.execute(
            """SELECT e.*, g.name AS guardian_name 
               FROM equipment e
               LEFT JOIN guardians g ON e.guardian_id = g.id
               WHERE e.id = ?""", 
            (equipment_id,)
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_all(type_filter=None, rarity_filter=None, unequipped_only=False):
        """取得所有裝備，支援類別、稀有度、未裝備篩選"""
        db = get_db_connection()
        query = """SELECT e.*, g.name AS guardian_name 
                   FROM equipment e
                   LEFT JOIN guardians g ON e.guardian_id = g.id
                   WHERE 1=1"""
        params = []
        
        if type_filter:
            query += " AND e.type = ?"
            params.append(type_filter)
            
        if rarity_filter:
            query += " AND e.rarity = ?"
            params.append(rarity_filter)
            
        if unequipped_only:
            query += " AND e.guardian_id IS NULL"
            
        query += " ORDER BY CASE rarity WHEN 'Legendary' THEN 1 WHEN 'Epic' THEN 2 WHEN 'Rare' THEN 3 ELSE 4 END, level DESC, id DESC"
        
        rows = db.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def delete(equipment_id):
        """刪除裝備"""
        db = get_db_connection()
        try:
            db.execute("DELETE FROM equipment WHERE id = ?", (equipment_id,))
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False

    @staticmethod
    def equip(equipment_id, guardian_id):
        """將裝備穿到守護靈身上。如果該槽位已有裝備，呼叫者會先將其拔下。"""
        db = get_db_connection()
        try:
            db.execute(
                "UPDATE equipment SET guardian_id = ? WHERE id = ?",
                (guardian_id, equipment_id)
            )
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False

    @staticmethod
    def unequip(equipment_id):
        """卸下裝備"""
        db = get_db_connection()
        try:
            db.execute(
                "UPDATE equipment SET guardian_id = NULL WHERE id = ?",
                (equipment_id,)
            )
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False

    @staticmethod
    def get_upgrade_cost(level, rarity):
        """計算裝備強化所需金幣"""
        rarity_multiplier = {
            'Common': 1.0,
            'Rare': 1.5,
            'Epic': 2.5,
            'Legendary': 4.0
        }
        mult = rarity_multiplier.get(rarity, 1.0)
        return int(level * 500 * mult)

    @staticmethod
    def upgrade(equipment_id):
        """強化裝備，消耗金幣，提升等級與屬性加成"""
        db = get_db_connection()
        equip = EquipmentModel.get_by_id(equipment_id)
        if not equip:
            return False, "裝備不存在！"
            
        cost = EquipmentModel.get_upgrade_cost(equip['level'], equip['rarity'])
        
        # 扣除金幣
        success, res = PlayerModel.update_resources(-cost, 0)
        if not success:
            return False, f"金幣不足！需要 {cost} 金幣。"
            
        new_level = equip['level'] + 1
        
        # 計算屬性增量
        # 根據種類與稀有度提升
        rarity_scale = {
            'Common': 1.0,
            'Rare': 1.3,
            'Epic': 1.8,
            'Legendary': 2.5
        }
        scale = rarity_scale.get(equip['rarity'], 1.0)
        
        new_hp_bonus = equip['hp_bonus']
        new_atk_bonus = equip['atk_bonus']
        new_def_bonus = equip['def_bonus']
        
        if equip['type'] == 'weapon':
            new_atk_bonus += int(8 * scale)
            new_hp_bonus += int(15 * scale)
        elif equip['type'] == 'armor':
            new_def_bonus += int(6 * scale)
            new_hp_bonus += int(40 * scale)
        elif equip['type'] == 'accessory':
            new_hp_bonus += int(25 * scale)
            new_atk_bonus += int(3 * scale)
            new_def_bonus += int(2 * scale)
            
        try:
            db.execute(
                """UPDATE equipment 
                   SET level = ?, hp_bonus = ?, atk_bonus = ?, def_bonus = ? 
                   WHERE id = ?""",
                (new_level, new_hp_bonus, new_atk_bonus, new_def_bonus, equipment_id)
            )
            db.commit()
            return True, {
                "equipment_id": equipment_id,
                "name": equip['name'],
                "old_level": equip['level'],
                "new_level": new_level,
                "gold_spent": cost,
                "hp_bonus": new_hp_bonus,
                "atk_bonus": new_atk_bonus,
                "def_bonus": new_def_bonus
            }
        except Exception as e:
            db.rollback()
            return False, f"強化裝備資料庫更新失敗: {str(e)}"
