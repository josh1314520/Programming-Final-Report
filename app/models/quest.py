import json
import sqlite3
from datetime import datetime
from app.database import get_db_connection

class Quest:
    """
    任務模型，負責主線任務、子目標、冒險者任務狀態進度及表單提交的資料庫處理。
    """

    @staticmethod
    def get_all(adventurer_id=1):
        """
        取得所有主線任務以及當前冒險者的進行狀態與子目標。
        
        :param adventurer_id: 冒險者 ID
        :return: 任務列表 (list of dict)
        """
        conn = get_db_connection()
        
        # 1. 取得所有任務定義
        quest_rows = conn.execute(
            "SELECT id, title, description, story_intro, reward_gold, reward_exp, prerequisite_quest_id, display_order FROM quests ORDER BY display_order ASC, id ASC;"
        ).fetchall()
        
        quests = []
        for q_row in quest_rows:
            q_dict = dict(q_row)
            quest_id = q_dict['id']
            
            # 2. 取得冒險者對應此任務的進度狀態
            status_row = conn.execute(
                "SELECT status, accepted_at, completed_at FROM adventurer_quests WHERE adventurer_id = ? AND quest_id = ?;",
                (adventurer_id, quest_id)
            ).fetchone()
            
            if status_row:
                q_dict['status'] = status_row['status']
                q_dict['accepted_at'] = status_row['accepted_at']
                q_dict['completed_at'] = status_row['completed_at']
            else:
                # 預設為鎖定狀態
                q_dict['status'] = 'locked'
                q_dict['accepted_at'] = None
                q_dict['completed_at'] = None
                
            # 3. 取得此任務關聯的所有子目標
            obj_rows = conn.execute(
                "SELECT id, description, code_identifier FROM quest_objectives WHERE quest_id = ? ORDER BY id ASC;",
                (quest_id,)
            ).fetchall()
            q_dict['objectives'] = [dict(obj) for obj in obj_rows]
            
            # 4. 如果有表單提交紀錄，也一併傳回 (已完成狀態)
            if q_dict['status'] == 'completed':
                sub_row = conn.execute(
                    "SELECT submitted_data, submitted_at FROM quest_submissions WHERE adventurer_id = ? AND quest_id = ? ORDER BY id DESC LIMIT 1;",
                    (adventurer_id, quest_id)
                ).fetchone()
                if sub_row:
                    try:
                        q_dict['submitted_data'] = json.loads(sub_row['submitted_data'])
                    except Exception:
                        q_dict['submitted_data'] = sub_row['submitted_data']
                    q_dict['submitted_at'] = sub_row['submitted_at']
            else:
                q_dict['submitted_data'] = None
                q_dict['submitted_at'] = None
                
            quests.append(q_dict)
            
        return quests

    @staticmethod
    def get_by_id(quest_id, adventurer_id=1):
        """
        取得特定任務的詳細定義與冒險者狀態。
        """
        quests = Quest.get_all(adventurer_id)
        for q in quests:
            if q['id'] == quest_id:
                return q
        return None

    @staticmethod
    def accept_quest(adventurer_id, quest_id):
        """
        接取主線任務 (狀態由 available 變更為 active)。
        
        :param adventurer_id: 冒險者 ID
        :param quest_id: 任務 ID
        :return: (Boolean, Message)
        """
        conn = get_db_connection()
        
        # 1. 檢查任務是否存在
        quest = Quest.get_by_id(quest_id, adventurer_id)
        if not quest:
            return False, "該任務不存在！"
            
        # 2. 驗證目前狀態是否為 available
        if quest['status'] != 'available':
            return False, f"任務無法接取！目前狀態為：{quest['status']}"
            
        # 3. 更新狀態為 active (進行中)
        now_str = datetime.now().isoformat()
        conn.execute(
            """
            INSERT OR REPLACE INTO adventurer_quests (adventurer_id, quest_id, status, accepted_at)
            VALUES (?, ?, 'active', ?);
            """,
            (adventurer_id, quest_id, now_str)
        )
        conn.commit()
        
        return True, f"成功接取任務：{quest['title']}！"

    @staticmethod
    def complete_quest(adventurer_id, quest_id, form_data):
        """
        提交表單並完成任務 (狀態由 active 變更為 completed)。
        儲存表單資料至 quest_submissions。
        自動解鎖下一階段的前置任務（將鎖定狀態 'locked' 變更為 'available'）。
        
        :param adventurer_id: 冒險者 ID
        :param quest_id: 任務 ID
        :param form_data: 提交的表單內容 (dict)
        :return: (Boolean, ResultDict)
        """
        conn = get_db_connection()
        
        # 1. 檢查任務狀態
        quest = Quest.get_by_id(quest_id, adventurer_id)
        if not quest:
            return False, {"error": "任務不存在！"}
            
        if quest['status'] != 'active':
            return False, {"error": f"任務必須是進行中狀態才能提交！目前狀態為：{quest['status']}"}
            
        now_str = datetime.now().isoformat()
        serialized_data = json.dumps(form_data, ensure_ascii=False)
        
        # 2. 寫入提交記錄
        conn.execute(
            """
            INSERT INTO quest_submissions (adventurer_id, quest_id, submitted_data, submitted_at)
            VALUES (?, ?, ?, ?);
            """,
            (adventurer_id, quest_id, serialized_data, now_str)
        )
        
        # 3. 將任務狀態改為已完成
        conn.execute(
            """
            UPDATE adventurer_quests 
            SET status = 'completed', completed_at = ? 
            WHERE adventurer_id = ? AND quest_id = ?;
            """,
            (now_str, adventurer_id, quest_id)
        )
        
        # 4. 自動尋找並解鎖以此任務為前置的所有任務
        unlock_rows = conn.execute(
            "SELECT id FROM quests WHERE prerequisite_quest_id = ?;",
            (quest_id,)
        ).fetchall()
        
        for unlock in unlock_rows:
            target_quest_id = unlock['id']
            # 檢查該解鎖任務目前的狀態
            chk_row = conn.execute(
                "SELECT status FROM adventurer_quests WHERE adventurer_id = ? AND quest_id = ?;",
                (adventurer_id, target_quest_id)
            ).fetchone()
            
            # 如果是 locked 或是尚未有記錄，則將其更新/插入為 available
            if not chk_row or chk_row['status'] == 'locked':
                conn.execute(
                    """
                    INSERT OR REPLACE INTO adventurer_quests (adventurer_id, quest_id, status)
                    VALUES (?, ?, 'available');
                    """,
                    (adventurer_id, target_quest_id)
                )
                
        conn.commit()
        
        return True, {
            "title": quest['title'],
            "reward_gold": quest['reward_gold'],
            "reward_exp": quest['reward_exp']
        }

    @staticmethod
    def create_custom_quest(title, description, story_intro, reward_gold, reward_exp, prerequisite_quest_id=None, objectives=None):
        """
        輔助方法：供使用者在前端動態建立全新任務，靈活擴充任務鏈。
        
        :param title: 任務名稱
        :param description: 任務說明
        :param story_intro: 劇情簡介
        :param reward_gold: 金幣獎勵
        :param reward_exp: 經驗值獎勵
        :param prerequisite_quest_id: 前置任務 ID (可空)
        :param objectives: 子目標清單 (list of dict, 包含 'description' 與 'code_identifier')
        :return: 建立的任務 ID
        """
        conn = get_db_connection()
        
        # 1. 取得最大 display_order
        max_order_row = conn.execute("SELECT MAX(display_order) as max_o FROM quests;").fetchone()
        next_order = (max_order_row['max_o'] or 0) + 1
        
        # 2. 插入任務定義
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quests (title, description, story_intro, reward_gold, reward_exp, prerequisite_quest_id, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (title, description, story_intro, reward_gold, reward_exp, prerequisite_quest_id, next_order)
        )
        quest_id = cursor.lastrowid
        
        # 3. 插入子目標
        if objectives:
            for obj in objectives:
                cursor.execute(
                    """
                    INSERT INTO quest_objectives (quest_id, description, code_identifier)
                    VALUES (?, ?, ?);
                    """,
                    (quest_id, obj['description'], obj['code_identifier'])
                )
                
        # 4. 對於所有現有冒險者，如果無前置任務，則預設狀態為 available，否則為 locked
        # 為了簡化，在我們的單人測試中，直接更新冒險者 1 的進度表
        adventurer_ids = [row['id'] for row in conn.execute("SELECT id FROM adventurers;").fetchall()]
        for adv_id in adventurer_ids:
            if prerequisite_quest_id:
                # 檢查前置任務是否完成，若已完成，則設為 available，否則鎖定
                pre_chk = conn.execute(
                    "SELECT status FROM adventurer_quests WHERE adventurer_id = ? AND quest_id = ?;",
                    (adv_id, prerequisite_quest_id)
                ).fetchone()
                status = 'available' if (pre_chk and pre_chk['status'] == 'completed') else 'locked'
            else:
                status = 'available'
                
            cursor.execute(
                """
                INSERT OR REPLACE INTO adventurer_quests (adventurer_id, quest_id, status)
                VALUES (?, ?, ?);
                """,
                (adv_id, quest_id, status)
            )
            
        conn.commit()
        return quest_id
