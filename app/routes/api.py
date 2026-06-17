import re
import threading
import math
import random
import json
from flask import Blueprint, jsonify, request
from app.models.adventurer import Adventurer
from app.models.quest import Quest
from app.models.vault import get_vault_status, update_vault_status, reset_vault_status
from app.models.report import create_report, get_all_reports, get_report_by_id

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 全域執行緒鎖，用以防止併發重複提交請求（Race Condition）
submit_lock = threading.Lock()

# ==========================================================
# 1. 冒險者主線任務模組 (Quest System APIs)
# ==========================================================

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
                "exp": reward_exp
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

# ==========================================================
# 2. 金庫資產與災難壓力測試模組 (Simulation & Vault APIs)
# ==========================================================

@api_bp.route('/vault', methods=['GET'])
def api_get_vault():
    """
    API：獲取當前金庫資產狀況。
    """
    vault = get_vault_status()
    if vault:
        return jsonify({"success": True, "vault": vault})
    return jsonify({"success": False, "message": "無法取得金庫狀態"}), 500

@api_bp.route('/vault/reset', methods=['POST'])
def api_reset_vault():
    """
    API：一鍵重設金庫資產至初始全滿狀態。
    """
    if reset_vault_status():
        vault = get_vault_status()
        return jsonify({"success": True, "message": "金庫資產已恢復全滿狀態", "vault": vault})
    return jsonify({"success": False, "message": "重置金庫失敗"}), 500

@api_bp.route('/reports', methods=['GET'])
def api_get_reports():
    """
    API：獲取歷史壓力測試報告列表。
    """
    reports = get_all_reports()
    return jsonify({"success": True, "reports": reports})

@api_bp.route('/reports/<int:report_id>', methods=['GET'])
def api_get_report_detail(report_id):
    """
    API：獲取單筆歷史測試報告的詳細資料與 24 個月折線數據。
    """
    report = get_report_by_id(report_id)
    if report:
        return jsonify({"success": True, "report": report})
    return jsonify({"success": False, "message": "找不到該筆壓力測試報告"}), 404

@api_bp.route('/simulate', methods=['POST'])
def api_simulate():
    """
    API：運行 24 個月時空背景下「資產風險壓力測試」演算法。
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "請提供模擬參數"}), 400

    disaster_type = data.get('disaster_type')
    portfolio = data.get('portfolio', {})
    upgrades = data.get('upgrades', [])

    # 1. 驗證資產比例總和是否為 100%
    gold_pct = float(portfolio.get('gold', 0))
    mana_pct = float(portfolio.get('mana_crystals', 0))
    bonds_pct = float(portfolio.get('bonds', 0))
    eggs_pct = float(portfolio.get('dragon_eggs', 0))
    supplies_pct = float(portfolio.get('supplies', 0))

    total_pct = gold_pct + mana_pct + bonds_pct + eggs_pct + supplies_pct
    if abs(total_pct - 100.0) > 0.01:
        return jsonify({"success": False, "message": "各項資產配置比例總和必須恰好等於 100%"}), 400

    # 2. 獲取目前 SQLite 中的金庫資源，計算目前金庫總體金幣等估值
    vault = get_vault_status()
    if not vault:
        return jsonify({"success": False, "message": "資料庫讀取異常"}), 500

    init_vault_val = (
        vault['gold'] * 1 +
        vault['mana_crystals'] * 10 +
        vault['bonds'] * 5 +
        vault['dragon_eggs'] * 50 +
        vault['supplies'] * 2
    )

    # 用來模擬 24 個月折線數據，初始總資產設為 10000 點以作為標準指數
    base_val = 10000.0
    v_gold = base_val * (gold_pct / 100.0)
    v_mana = base_val * (mana_pct / 100.0)
    v_bonds = base_val * (bonds_pct / 100.0)
    v_eggs = base_val * (eggs_pct / 100.0)
    v_supplies = base_val * (supplies_pct / 100.0)

    # 3. 24 個月壓力測試時間序列演算法
    chart_data = [{"month": 0, "value": base_val, "gold": v_gold, "mana": v_mana, "bonds": v_bonds, "eggs": v_eggs, "supplies": v_supplies}]
    
    max_mdd = 0.0
    min_val = base_val
    peak_val = base_val
    recovery_month = -1

    for month in range(1, 25):
        noise = random.uniform(-0.01, 0.01)

        r_gold = 0.001
        r_mana = 0.005
        r_bonds = 0.002
        r_eggs = 0.008
        r_supplies = 0.001

        if disaster_type == "2008 年矮人銀行金融海嘯":
            if 2 <= month <= 8:
                drop = -0.05
                if "guild_insurance" in upgrades:
                    drop = drop * 0.4
                r_bonds += drop
            elif month > 8:
                r_bonds += 0.01

            if 1 <= month <= 12:
                r_mana += -0.055
            else:
                r_mana += 0.02

            if 1 <= month <= 9:
                r_eggs += -0.09
            else:
                r_eggs += 0.03

            if 1 <= month <= 10:
                gold_gain = 0.018
                if "gold_hedge" in upgrades:
                    gold_gain += 0.008
                r_gold += gold_gain
            else:
                r_gold += 0.003

            if 1 <= month <= 8:
                r_supplies += -0.02
            else:
                r_supplies += 0.005

        elif disaster_type == "2020 年魔力瘟疫疫情大爆發":
            if 1 <= month <= 3:
                r_gold += -0.01
                r_bonds += -0.015
                r_eggs += -0.08
                crystal_drop = -0.09
                if "shield_overdrive" in upgrades:
                    crystal_drop = -0.03
                r_mana += crystal_drop
                r_supplies += -0.02
            else:
                supp_gain = 0.065
                if "cold_chain" in upgrades:
                    supp_gain += 0.025
                r_supplies += supp_gain
                r_mana += 0.045
                r_bonds += 0.005
                r_gold += 0.008
                r_eggs += random.choice([-0.04, 0.06, -0.02, 0.08])

        elif disaster_type == "2000 年魔導科技泡沫破裂":
            if 1 <= month <= 15:
                mana_drop = -0.085
                if "shield_overdrive" in upgrades:
                    mana_drop = -0.035
                r_mana += mana_drop
            else:
                r_mana += 0.01

            if 1 <= month <= 10:
                r_eggs += -0.05
            else:
                r_eggs += 0.01

            r_gold += 0.008 if month <= 12 else 0.002
            r_bonds += 0.003
            r_supplies += 0.001

        elif disaster_type == "1929 年精靈帝國大蕭條":
            if 1 <= month <= 16:
                r_mana += -0.05
                r_eggs += -0.09
                bond_drop = -0.035
                if "guild_insurance" in upgrades:
                    bond_drop = -0.012
                r_bonds += bond_drop
                r_supplies += -0.04
                gold_gain = 0.01
                if "gold_hedge" in upgrades:
                    gold_gain += 0.01
                r_gold += gold_gain
            else:
                r_mana += 0.01
                r_eggs += 0.015
                r_bonds += 0.005
                r_supplies += 0.01
                r_gold += 0.002

        v_gold = max(0.0, v_gold * (1 + r_gold + noise))
        v_mana = max(0.0, v_mana * (1 + r_mana + noise))
        v_bonds = max(0.0, v_bonds * (1 + r_bonds + noise))
        v_eggs = max(0.0, v_eggs * (1 + r_eggs + noise))
        v_supplies = max(0.0, v_supplies * (1 + r_supplies + noise))

        current_total = v_gold + v_mana + v_bonds + v_eggs + v_supplies
        
        if current_total > peak_val:
            peak_val = current_total
            
        current_drawdown = ((peak_val - current_total) / peak_val) * 100.0
        if current_drawdown > max_mdd:
            max_mdd = current_drawdown

        if current_total < min_val:
            min_val = current_total

        if recovery_month == -1 and current_total >= base_val and month >= 3:
            recovery_month = month

        chart_data.append({
            "month": month,
            "value": round(current_total, 2),
            "gold": round(v_gold, 2),
            "mana": round(v_mana, 2),
            "bonds": round(v_bonds, 2),
            "eggs": round(v_eggs, 2),
            "supplies": round(v_supplies, 2)
        })

    if recovery_month == -1:
        recovery_month = 25

    final_total_val = chart_data[-1]["value"]
    net_performance_ratio = final_total_val / base_val

    advice_list = []
    
    if max_mdd > 45.0:
        advice_list.append("🚨 **金庫極高危警告**：本次模擬中，您的最大資產縮水幅度高達 **{:.2f}%**！這是極為致命的財務打擊。".format(max_mdd))
    elif max_mdd > 20.0:
        advice_list.append("⚠️ **金庫中度風險警示**：最大資產縮水達 **{:.2f}%**。雖然在承受範圍內，但仍有改善空間。".format(max_mdd))
    else:
        advice_list.append("🛡️ **金庫大師級防守**：最大資產縮水僅 **{:.2f}%**，這在史詩級海嘯中屬於極度優秀的避險表現！".format(max_mdd))

    if disaster_type == "2008 年矮人銀行金融海嘯":
        if bonds_pct > 25 and "guild_insurance" not in upgrades:
            advice_list.append("📜 **公債缺漏**：您配置了 {:.0f}% 的「皇家公債」，但在銀行海嘯中公債大跌且未加購「公會存託保險」，使您的安全資產慘遭無效對沖。建議下次務必勾選保險。".format(bonds_pct))
        if mana_pct + eggs_pct > 40:
            advice_list.append("🔮 **投機泡影**：魔力水晶與飛龍蛋總佔比達 {:.0f}%。在流動性黑洞中，這類高風險資產遭到清算，強烈建議將部分比例轉至「實體黃金」以作避風港。".format(mana_pct + eggs_pct))
        if "gold_hedge" in upgrades:
            advice_list.append("✨ **對沖點評**：您購買的『實體黃金對沖』在黃金狂飆時發揮了極佳的增益，成功收復了部分高風險板塊的失地！")
            
    elif disaster_type == "2020 年魔力瘟疫疫情大爆發":
        if supplies_pct < 15:
            advice_list.append("🌾 **糧草告急**：您的「冒險糧草物資」佔比僅 {:.0f}%。瘟疫肆虐時物資需求極大、價格狂飆，您卻因為配置過低而未能充分享受這波暴漲紅利。".format(supplies_pct))
        elif "cold_chain" not in upgrades:
            advice_list.append("🦠 **物資腐爛**：您囤積了物資，但未購買「強化冷鏈糧倉」，導致疫情初期隔離期間，大量食物因倉儲不力腐壞變質，利潤大打折扣。建議下次加購。")
        if mana_pct > 25 and "shield_overdrive" not in upgrades:
            advice_list.append("📡 **水晶衝擊**：您的魔力水晶在疫情爆發初期劇烈波動，若加裝「魔法護盾過載協議」將能大幅縮減初期 25% 的回檔，並更安全地迎接後續的 V 型反彈。")

    elif disaster_type == "2000 年魔導科技泡沫破裂":
        if mana_pct > 30:
            if "shield_overdrive" not in upgrades:
                advice_list.append("💥 **水晶破滅**：科技泡沫對您的「魔力水晶」造成了 80% 的毀滅性降維打擊！您未購買「魔法護盾過載協議」，導致金庫價值在第 10 個月時幾乎蒸發。")
            else:
                advice_list.append("🛡️ **過載防禦**：幸好您開啟了『魔法護盾過載協議』，成功將魔力水晶的跌幅減半，為整個公會爭取了極大的生存空間！")
        if gold_pct < 20:
            advice_list.append("🪙 **黃金防衛不足**：在此次泡沫中，黃金保持極佳穩定性。若能將黃金配置比例提升至 20% 以上，將大幅平滑您的資產波動曲線。")

    elif disaster_type == "1929 年精靈帝國大蕭條":
        if gold_pct < 35:
            advice_list.append("🕯️ **大蕭條嚴寒**：這是一場為期 16 個月的全面性冰封通縮！在此情境下，唯有「實體黃金」能自保。您的黃金佔比過低（{:.0f}%），導致恢復期極度拉長（需 {} 個月）。下次建議黃金至少配置 35% 以上。".format(gold_pct, "24+" if recovery_month >= 25 else recovery_month))
        else:
            advice_list.append("👑 **黃金王者**：完美的通縮抗性！高比例的黃金配置讓您在大蕭條的嚴冬中依然手握充足的流動資金。")

    if recovery_month >= 25:
        advice_list.append("⌛ **漫長嚴冬**：您的投資組合在此次危機中受創極深，在模擬的 24 個月內**無法恢復至初始總值**！防禦工事急需重整。")
    else:
        advice_list.append("⏳ **復甦時間**：您的資產在危機爆發後的第 **{}** 個月成功收復失地、重回巔峰。避險策略反應迅速。".format(recovery_month))

    hedging_advice = "\n\n".join(advice_list)

    new_gold = max(10, int(vault['gold'] * net_performance_ratio))
    new_mana = max(10, int(vault['mana_crystals'] * net_performance_ratio))
    new_bonds = max(10, int(vault['bonds'] * net_performance_ratio))
    new_eggs = max(5, int(vault['dragon_eggs'] * net_performance_ratio))
    new_supplies = max(10, int(vault['supplies'] * net_performance_ratio))
    
    new_gold = min(50000, new_gold)
    new_mana = min(50000, new_mana)
    new_bonds = min(50000, new_bonds)
    new_eggs = min(10000, new_eggs)
    new_supplies = min(50000, new_supplies)

    update_vault_status(new_gold, new_mana, new_bonds, new_eggs, new_supplies)

    report_id = create_report(
        disaster_type=disaster_type,
        portfolio_distribution=portfolio,
        hedging_upgrades=upgrades,
        max_drawdown=round(max_mdd, 2),
        recovery_period=recovery_month,
        initial_total_val=round(base_val, 2),
        min_total_val=round(min_val, 2),
        final_total_val=round(final_total_val, 2),
        hedging_advice=hedging_advice,
        chart_data=chart_data
    )

    updated_vault = get_vault_status()

    return jsonify({
        "success": True,
        "report_id": report_id,
        "max_drawdown": round(max_mdd, 2),
        "recovery_period": recovery_month,
        "initial_total_val": round(base_val, 2),
        "min_total_val": round(min_val, 2),
        "final_total_val": round(final_total_val, 2),
        "hedging_advice": hedging_advice,
        "chart_data": chart_data,
        "updated_vault": updated_vault
    })
