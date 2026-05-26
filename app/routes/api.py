import re
import threading
from flask import Blueprint, jsonify, request
from app.models.adventurer import Adventurer
from app.models.quest import Quest

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 全域執行緒鎖，用以防止併發重複提交請求（Race Condition）
submit_lock = threading.Lock()

@api_bp.route('/adventurer', methods=['GET'])
def get_adventurer():
    """
    取得冒險者角色狀態 (等級、經驗值、金幣、稱號)。
    """
    try:
        adv = Adventurer.get_by_id(1)  # 專案預設玩家 ID=1
        if adv:
            return jsonify({"success": True, "adventurer": adv})
        return jsonify({"success": False, "error": "冒險者未尋獲"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": f"系統錯誤: {str(e)}"}), 500

@api_bp.route('/quests', methods=['GET'])
def get_quests():
    """
    取得所有主線任務、當前玩家的接取狀態與關聯的子目標。
    """
    try:
        quests = Quest.get_all(1)  # 專案預設玩家 ID=1
        return jsonify({"success": True, "quests": quests})
    except Exception as e:
        return jsonify({"success": False, "error": f"系統錯誤: {str(e)}"}), 500

@api_bp.route('/quests/<int:quest_id>/accept', methods=['POST'])
def accept_quest(quest_id):
    """
    接取任務，將狀態變更為進行中 (active)。
    """
    try:
        success, message = Quest.accept_quest(adventurer_id=1, quest_id=quest_id)
        if success:
            return jsonify({"success": True, "message": message})
        return jsonify({"success": False, "error": message}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"系統錯誤: {str(e)}"}), 500

@api_bp.route('/quests/<int:quest_id>/submit', methods=['POST'])
def submit_quest(quest_id):
    """
    提交劇情式任務表單（執行緒安全包裝）。
    """
    with submit_lock:
        return _submit_quest_locked(quest_id)

def _submit_quest_locked(quest_id):
    """
    實際執行劇情式任務表單提交邏輯。
    """
    try:
        data = request.get_json() or {}
        
        # [防刷機制] 1. 先從資料庫檢查該任務狀態是否已完成或非進行中，避免惡意重複發送 POST 請求領取獎勵
        quest = Quest.get_by_id(quest_id, 1)
        if not quest:
            return jsonify({"success": False, "error": "此任務不存在"}), 404
            
        if quest['status'] == 'completed':
            return jsonify({
                "success": False, 
                "error": "此主線任務已完成，請勿重複提交以刷取金幣與經驗值！"
            }), 400
            
        if quest['status'] != 'active':
            return jsonify({
                "success": False, 
                "error": f"任務必須是進行中狀態才能提交！目前狀態為：{quest['status']}"
            }), 400
            
        # 2. 根據任務 ID 進行個別的劇情欄位驗證
        if quest_id == 1:
            # ----------------------------------------------------
            # 開戶任務 (契約之印) 欄位驗證
            # ----------------------------------------------------
            real_name = data.get('real_name', '').strip()
            character_class = data.get('character_class', '').strip()
            vault_password = data.get('vault_password', '')
            license_number = data.get('license_number', '').strip()
            
            if not real_name or len(real_name) < 2:
                return jsonify({
                    "success": False, 
                    "error": "冒險真名為必填欄位，且長度必須大於或等於 2 個字！"
                }), 400
                
            valid_classes = ['Warrior', 'Mage', 'Rogue', 'Cleric']
            if character_class not in valid_classes:
                return jsonify({
                    "success": False, 
                    "error": "守護職業無效！必須是 戰士(Warrior)、法師(Mage)、盜賊(Rogue) 或 牧師(Cleric) 之一。"
                }), 400
                
            if not vault_password or len(vault_password) < 6:
                return jsonify({
                    "success": False, 
                    "error": "安全金庫密碼至少需要 6 個字元以上！"
                }), 400
                
            # 驗證執照格式: ADV-XXXXX (例如: ADV-12345)
            if not license_number or not re.match(r'^ADV-\d{5}$', license_number):
                return jsonify({
                    "success": False, 
                    "error": "冒險者執照編號格式錯誤！正確格式應為 'ADV-' 後接 5 碼數字，例如：ADV-88888"
                }), 400
                
        elif quest_id == 2:
            # ----------------------------------------------------
            # 保單分析任務 (命運之御) 欄位驗證
            # ----------------------------------------------------
            risk_level = data.get('risk_level', '').strip()
            coverage_amount = data.get('coverage_amount')
            insurance_types = data.get('insurance_types', [])
            
            valid_risks = ['low', 'medium', 'high']
            if risk_level not in valid_risks:
                return jsonify({
                    "success": False, 
                    "error": "請選擇有效的風險評估等級 (高風險/中風險/低風險)！"
                }), 400
                
            try:
                coverage_amount = int(coverage_amount)
            except (ValueError, TypeError):
                return jsonify({
                    "success": False, 
                    "error": "保險保障額度必須為有效的整數數字！"
                }), 400
                
            if coverage_amount < 10000 or coverage_amount > 1000000:
                return jsonify({
                    "success": False, 
                    "error": "保險額度不合理！額度範圍必須在 10,000 到 1,000,000 金幣之間。"
                }), 400
                
            if not isinstance(insurance_types, list) or len(insurance_types) == 0:
                return jsonify({
                    "success": False, 
                    "error": "請至少選擇一項主要投保險種 (例如：人身意外險、裝備損毀險)！"
                }), 400
        else:
            # ----------------------------------------------------
            # 自訂/擴充主線任務驗證 (動態檢查所有子目標欄位是否存在且不為空)
            # ----------------------------------------------------
            quest = Quest.get_by_id(quest_id, 1)
            if not quest:
                return jsonify({"success": False, "error": "此任務不存在"}), 404
                
            for obj in quest.get('objectives', []):
                val = data.get(obj['code_identifier'])
                if val is None or (isinstance(val, str) and not val.strip()):
                    return jsonify({
                        "success": False, 
                        "error": f"子目標尚未達成：未填寫『{obj['description']}』欄位！"
                    }), 400

        # 2. 呼叫 Quest Model 完成任務並取得獎勵設定
        success, complete_res = Quest.complete_quest(adventurer_id=1, quest_id=quest_id, form_data=data)
        if not success:
            return jsonify({"success": False, "error": complete_res.get("error", "任務完成失敗")}), 400
            
        reward_gold = complete_res['reward_gold']
        reward_exp = complete_res['reward_exp']
        quest_title = complete_res['title']
        
        # 3. 派發獎勵與升級演算
        stats = Adventurer.reward_adventurer(adventurer_id=1, gold_reward=reward_gold, exp_reward=reward_exp)
        
        # 4. 回傳精確的成功封包
        is_level_up = stats['is_level_up']
        level_ups_count = stats['level_ups_count']
        
        congrats_message = f"【史詩捷報】您成功完成了主線任務《{quest_title}》！"
        if is_level_up:
            congrats_message += f" 恭喜您升級了！目前已晉升為『{stats['title']}』(Lv.{stats['level']})！"
        else:
            congrats_message += f" 獲得了 {reward_gold} 金幣與 {reward_exp} 經驗值！"

        return jsonify({
            "success": True,
            "message": congrats_message,
            "rewards": {
                "gold": reward_gold,
                "exp": exp_reward
            },
            "new_stats": {
                "level": stats['level'],
                "exp": stats['exp'],
                "gold": stats['gold'],
                "title": stats['title'],
                "is_level_up": is_level_up,
                "level_ups_count": level_ups_count
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"系統錯誤: {str(e)}"}), 500

@api_bp.route('/quests/create', methods=['POST'])
def create_quest():
    """
    自訂主線任務建立 API (供後續隨意擴展)。
    """
    try:
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        story_intro = data.get('story_intro', '').strip()
        reward_gold = int(data.get('reward_gold', 0))
        reward_exp = int(data.get('reward_exp', 0))
        prerequisite_quest_id = data.get('prerequisite_quest_id')
        objectives = data.get('objectives', []) # [{"description": "...", "code_identifier": "..."}]
        
        if not title or not description or not story_intro:
            return jsonify({"success": False, "error": "標題、說明與故事背景為必填欄位！"}), 400
            
        if not objectives or len(objectives) == 0:
            return jsonify({"success": False, "error": "自訂主線任務必須包含至少一個子目標！"}), 400
            
        quest_id = Quest.create_custom_quest(
            title=title,
            description=description,
            story_intro=story_intro,
            reward_gold=reward_gold,
            reward_exp=reward_exp,
            prerequisite_quest_id=prerequisite_quest_id,
            objectives=objectives
        )
        
        return jsonify({
            "success": True, 
            "message": f"成功建立史詩主線任務《{title}》(ID: {quest_id})，已加入公會主線進度表！",
            "quest_id": quest_id
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"系統錯誤: {str(e)}"}), 500
