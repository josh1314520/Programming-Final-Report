import sqlite3
from app.database import get_db_connection

class Adventurer:
    """
    冒險者模型，處理冒險者角色的 CRUD 與遊戲化狀態（經驗值、金幣、等級、稱號）。
    """
    
    @staticmethod
    def get_by_id(adventurer_id=1):
        """
        取得指定 ID 的冒險者屬性。
        預設取得系統唯一的測試帳號 ID = 1 ('Hero')。
        """
        conn = get_db_connection()
        row = conn.execute(
            "SELECT id, username, level, exp, gold, title FROM adventurers WHERE id = ?;",
            (adventurer_id,)
        ).fetchone()
        
        if row:
            return dict(row)
        return None

    @staticmethod
    def get_title_by_level(level):
        """
        根據等級取得對應的冒險者稱號。
        """
        if level <= 2:
            return "見習冒險者"
        elif level <= 4:
            return "正式冒險者"
        elif level <= 7:
            return "精銳冒險者"
        elif level <= 9:
            return "傳奇冒險者"
        else:
            return "金庫史詩守護者"

    @staticmethod
    def reward_adventurer(adventurer_id, gold_reward, exp_reward):
        """
        派發任務完成獎勵：金幣與經驗值。
        實作循環升級偵測，處理經驗值溢出（可一次升多級）並自動更新稱號。
        
        :param adventurer_id: 冒險者 ID
        :param gold_reward: 獎勵金幣
        :param exp_reward: 獎勵經驗值
        :return: 包含最新屬性與升級資訊的字典
        """
        conn = get_db_connection()
        
        # 1. 取得當前屬性
        adv = Adventurer.get_by_id(adventurer_id)
        if not adv:
            raise ValueError(f"Adventurer with ID {adventurer_id} does not exist.")
            
        current_level = adv['level']
        current_exp = adv['exp'] + exp_reward
        current_gold = adv['gold'] + gold_reward
        
        # 2. 循環判斷是否升級
        # 升級公式：從 L 級升到 L+1 級需要 L * 100 的經驗值
        is_level_up = False
        level_ups_count = 0
        
        while current_exp >= (current_level * 100):
            current_exp -= (current_level * 100)
            current_level += 1
            is_level_up = True
            level_ups_count += 1
            
        # 3. 取得新稱號
        new_title = Adventurer.get_title_by_level(current_level)
        
        # 4. 更新資料庫
        conn.execute(
            """
            UPDATE adventurers 
            SET level = ?, exp = ?, gold = ?, title = ? 
            WHERE id = ?;
            """,
            (current_level, current_exp, current_gold, new_title, adventurer_id)
        )
        conn.commit()
        
        return {
            "level": current_level,
            "exp": current_exp,
            "gold": current_gold,
            "title": new_title,
            "is_level_up": is_level_up,
            "level_ups_count": level_ups_count,
            "rewards": {
                "gold": gold_reward,
                "exp": exp_reward
            }
        }
