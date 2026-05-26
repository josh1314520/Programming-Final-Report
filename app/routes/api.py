import math
import random
import json
from flask import Blueprint, jsonify, request
from app.models.vault import get_vault_status, update_vault_status, reset_vault_status
from app.models.report import create_report, get_all_reports, get_report_by_id

api_bp = Blueprint('api', __name__, url_prefix='/api')

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
    接收參數：
    - disaster_type (str): 災難類型
    - portfolio (dict): 資產佔比 (gold, mana_crystals, bonds, dragon_eggs, supplies 總和為 100)
    - upgrades (list): 已啟動的防禦/保險 (guild_insurance, cold_chain, shield_overdrive, gold_hedge)
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
    # 資源估值權重 (1個資產折合多少金幣)：
    # 金幣(1) / 水晶(10) / 公債(5) / 飛龍蛋(50) / 糧草(2)
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
    recovery_month = -1 # -1 表示未恢復

    # 根據不同歷史海嘯定義資產波動矩陣
    for month in range(1, 25):
        # 增加小幅度的隨機雜訊波動 [-1%, +1%] 增加擬真度
        noise = random.uniform(-0.01, 0.01)

        # 基礎月度收益率 (預設極微幅成長)
        r_gold = 0.001
        r_mana = 0.005
        r_bonds = 0.002
        r_eggs = 0.008
        r_supplies = 0.001

        # 災難衝擊波計算
        if disaster_type == "2008 年矮人銀行金融海嘯":
            # 皇家公債受信用海嘯重挫 (2-8個月)
            if 2 <= month <= 8:
                drop = -0.05
                if "guild_insurance" in upgrades:
                    drop = drop * 0.4 # 保險減少60%損失
                r_bonds += drop
            elif month > 8:
                r_bonds += 0.01 # 緩步復甦

            # 魔力水晶泡沫破裂，持續大跌 12 個月
            if 1 <= month <= 12:
                r_mana += -0.055
            else:
                r_mana += 0.02 # 後期修復

            # 飛龍蛋高風險投機斷頭潮，第1-9個月暴跌
            if 1 <= month <= 9:
                r_eggs += -0.09
            else:
                r_eggs += 0.03

            # 黃金避險需求激增
            if 1 <= month <= 10:
                gold_gain = 0.018
                if "gold_hedge" in upgrades:
                    gold_gain += 0.008 # 對沖增益
                r_gold += gold_gain
            else:
                r_gold += 0.003

            # 物資微幅萎縮
            if 1 <= month <= 8:
                r_supplies += -0.02
            else:
                r_supplies += 0.005

        elif disaster_type == "2020 年魔力瘟疫疫情大爆發":
            # 瘟疫爆發初期 (1-3月) 全資產流動性崩壞下跌
            if 1 <= month <= 3:
                r_gold += -0.01
                r_bonds += -0.015
                r_eggs += -0.08
                # 水晶初跌
                crystal_drop = -0.09
                if "shield_overdrive" in upgrades:
                    crystal_drop = -0.03 # 魔法盾減免
                r_mana += crystal_drop
                # 物資初期短暫封閉
                r_supplies += -0.02
            else:
                # 4個月後疫情各板塊分化
                # 物資暴漲
                supp_gain = 0.065
                if "cold_chain" in upgrades:
                    supp_gain += 0.025 # 冷鏈增益與零損耗
                r_supplies += supp_gain
                
                # 水晶強勢 V 型反彈 (遠距魔法需求)
                r_mana += 0.045
                
                # 公債避險回流穩定
                r_bonds += 0.005
                
                # 黃金平穩避險
                r_gold += 0.008
                
                # 飛龍蛋暴漲暴跌
                r_eggs += random.choice([-0.04, 0.06, -0.02, 0.08])

        elif disaster_type == "2000 年魔導科技泡沫破裂":
            # 魔力水晶泡沫破滅 (1-15個月崩跌)
            if 1 <= month <= 15:
                mana_drop = -0.085
                if "shield_overdrive" in upgrades:
                    mana_drop = -0.035 # 魔法盾過載抵擋
                r_mana += mana_drop
            else:
                r_mana += 0.01

            # 飛龍蛋投機板塊受波及跌
            if 1 <= month <= 10:
                r_eggs += -0.05
            else:
                r_eggs += 0.01

            # 公債與黃金溫和走強
            r_gold += 0.008 if month <= 12 else 0.002
            r_bonds += 0.003
            r_supplies += 0.001

        elif disaster_type == "1929 年精靈帝國大蕭條":
            # Relentless long-term deflationary collapse for all except gold
            if 1 <= month <= 16:
                r_mana += -0.05
                r_eggs += -0.09
                
                bond_drop = -0.035
                if "guild_insurance" in upgrades:
                    bond_drop = -0.012 # 保險減幅
                r_bonds += bond_drop

                r_supplies += -0.04
                
                gold_gain = 0.01
                if "gold_hedge" in upgrades:
                    gold_gain += 0.01
                r_gold += gold_gain
            else:
                # 緩慢爬坡
                r_mana += 0.01
                r_eggs += 0.015
                r_bonds += 0.005
                r_supplies += 0.01
                r_gold += 0.002

        # 應用月度收益率計算
        v_gold = max(0.0, v_gold * (1 + r_gold + noise))
        v_mana = max(0.0, v_mana * (1 + r_mana + noise))
        v_bonds = max(0.0, v_bonds * (1 + r_bonds + noise))
        v_eggs = max(0.0, v_eggs * (1 + r_eggs + noise))
        v_supplies = max(0.0, v_supplies * (1 + r_supplies + noise))

        current_total = v_gold + v_mana + v_bonds + v_eggs + v_supplies
        
        # 追蹤最高點與最大回檔率
        if current_total > peak_val:
            peak_val = current_total
            
        current_drawdown = ((peak_val - current_total) / peak_val) * 100.0
        if current_drawdown > max_mdd:
            max_mdd = current_drawdown

        # 追蹤最低點
        if current_total < min_val:
            min_val = current_total

        # 追蹤恢復期 (當回到初始 10000.0 以上時)
        if recovery_month == -1 and current_total >= base_val and month >= 3:
            # 至少模擬 3 個月後才可觸發恢復判定，防止第1個月微漲誤判
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

    # 若24個月結束仍未恢復，設定為 25 (代表 24+ 個月以上)
    if recovery_month == -1:
        recovery_month = 25

    final_total_val = chart_data[-1]["value"]
    net_performance_ratio = final_total_val / base_val # 大盤績效比

    # 4. 前端回饋：客製化避險建議 (羊皮紙內容生成)
    advice_list = []
    
    # 根據最大縮水評定
    if max_mdd > 45.0:
        advice_list.append("🚨 **金庫極高危警告**：本次模擬中，您的最大資產縮水幅度高達 **{:.2f}%**！這是極為致命的財務打擊。".format(max_mdd))
    elif max_mdd > 20.0:
        advice_list.append("⚠️ **金庫中度風險警示**：最大資產縮水達 **{:.2f}%**。雖然在承受範圍內，但仍有改善空間。".format(max_mdd))
    else:
        advice_list.append("🛡️ **金庫大師級防守**：最大資產縮水僅 **{:.2f}%**，這在史詩級海嘯中屬於極度優秀的避險表現！".format(max_mdd))

    # 根據資產比重與災難情境進行細緻反饋
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

    # 5. 遊戲化反饋：將模擬大盤績效比 (net_performance_ratio) 套用至當前 SQLite 中的金庫資源！
    # 讓玩家的投資操作、保險防禦與金庫資源真正產生深刻的連動效果！
    new_gold = max(10, int(vault['gold'] * net_performance_ratio))
    new_mana = max(10, int(vault['mana_crystals'] * net_performance_ratio))
    new_bonds = max(10, int(vault['bonds'] * net_performance_ratio))
    new_eggs = max(5, int(vault['dragon_eggs'] * net_performance_ratio))
    new_supplies = max(10, int(vault['supplies'] * net_performance_ratio))
    
    # 限制資源上限，防止無限翻倍溢出 (上限 50,000)
    new_gold = min(50000, new_gold)
    new_mana = min(50000, new_mana)
    new_bonds = min(50000, new_bonds)
    new_eggs = min(10000, new_eggs)
    new_supplies = min(50000, new_supplies)

    update_vault_status(new_gold, new_mana, new_bonds, new_eggs, new_supplies)

    # 6. 保存壓力測試報告至資料庫
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

    # 獲取更新後的金庫資產以回傳給前端
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
