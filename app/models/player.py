import sqlite3
from datetime import datetime
from app import get_db_connection

class PlayerModel:
    @staticmethod
    def get_player():
        """取得玩家資訊 (預設單一玩家 ID = 1)"""
        db = get_db_connection()
        row = db.execute("SELECT * FROM player WHERE id = 1").fetchone()
        if not row:
            # 如果不存在，建立一個
            db.execute("INSERT INTO player (id, gold, soul_stones) VALUES (1, 50000, 50)")
            db.commit()
            row = db.execute("SELECT * FROM player WHERE id = 1").fetchone()
        return dict(row)

    @staticmethod
    def update_resources(gold_change, stone_change):
        """更新玩家的金幣與靈石，若扣除後小於 0 則拒絕並回傳 False"""
        db = get_db_connection()
        player = PlayerModel.get_player()
        
        new_gold = player['gold'] + gold_change
        new_soul_stones = player['soul_stones'] + stone_change
        
        if new_gold < 0 or new_soul_stones < 0:
            return False, "資源不足！"
            
        try:
            db.execute(
                "UPDATE player SET gold = ?, soul_stones = ? WHERE id = 1",
                (new_gold, new_soul_stones)
            )
            db.commit()
            return True, {
                "gold": new_gold,
                "soul_stones": new_soul_stones,
                "gold_change": gold_change,
                "stone_change": stone_change
            }
        except Exception as e:
            db.rollback()
            return False, f"更新玩家資源失敗: {str(e)}"

    @staticmethod
    def claim_daily():
        """領取每日補給 (冷卻時間為 60 秒，以利展示測試)"""
        db = get_db_connection()
        player = PlayerModel.get_player()
        
        now = datetime.now()
        last_daily_str = player.get('last_daily')
        
        if last_daily_str:
            try:
                last_daily = datetime.fromisoformat(last_daily_str)
                # 60 秒測試冷卻
                cooldown_seconds = 60
                time_diff = (now - last_daily).total_seconds()
                if time_diff < cooldown_seconds:
                    remaining = int(cooldown_seconds - time_diff)
                    return False, f"補給傳送中！請等待 {remaining} 秒後再次領取。"
            except ValueError:
                pass # 解析失敗則忽略並允許領取
                
        # 增加 20000 金幣 與 10 靈石
        reward_gold = 20000
        reward_stones = 10
        
        new_gold = player['gold'] + reward_gold
        new_soul_stones = player['soul_stones'] + reward_stones
        
        try:
            db.execute(
                "UPDATE player SET gold = ?, soul_stones = ?, last_daily = ? WHERE id = 1",
                (new_gold, new_soul_stones, now.isoformat())
            )
            db.commit()
            return True, {
                "gold": new_gold,
                "soul_stones": new_soul_stones,
                "gold_added": reward_gold,
                "stones_added": reward_stones,
                "message": "成功引導虛空星海之力！獲得 20,000 金幣 與 10 靈石！"
            }
        except Exception as e:
            db.rollback()
            return False, f"領取每日補給失敗: {str(e)}"
