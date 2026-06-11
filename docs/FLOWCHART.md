# 主線任務系統 流程與序列圖設計

本文件包含使用者操作的 Flowchart 以及前後端資料互動的 Sequence Diagram。

## 1. 使用者操作流程 (User Flow)

描述冒險者進入系統、接取任務、填寫並提交劇情表單、獲取獎勵的完整生命週期：

```mermaid
flowchart TD
    Start([1. 進入冒險者金庫首頁]) --> FetchStatus[載入冒險者狀態與任務列表]
    FetchStatus --> CheckQuests{主線任務狀態?}
    
    %% 開戶任務流程
    CheckQuests -->|開戶任務未開始| AcceptOpen[點擊『簽訂契約之印』]
    AcceptOpen --> ShowOpenForm[顯示開戶表單視窗]
    ShowOpenForm --> FillOpen[填寫冒險者名字、職業、安全密碼、冒險執照]
    FillOpen --> SubmitOpen[點擊提交表單]
    
    %% 保單分析任務流程
    CheckQuests -->|保單分析任務鎖定| LockBtn[按鈕鎖定：需先完成開戶任務]
    CheckQuests -->|開戶任務完成 & 保單分析未開始| UnlockBtn[點擊『解鎖命運之御』]
    UnlockBtn --> ShowInsForm[顯示保單分析表單視窗]
    ShowInsForm --> FillIns[選擇風險等級、輸入期望保額、投保項目]
    FillIns --> SubmitIns[點擊提交表單]
    
    %% 提交表單後端處理與獎勵
    SubmitOpen --> BackendVerify{後端欄位驗證?}
    SubmitIns --> BackendVerify
    
    BackendVerify -->|格式不符| ShowError[彈出錯誤訊息視窗]
    ShowError --> FillOpen
    ShowError --> FillIns
    
    BackendVerify -->|驗證成功| ApplyRewards[更新 SQLite: 狀態設為已完成 + 增加金幣與經驗]
    ApplyRewards --> ReturnSuccess[回傳成功 JSON 訊息與最新冒險者數值]
    ReturnSuccess --> FEEffect[前端播放灑落金幣/粒子特效與音效]
    FEEffect --> UpdateStatsUI[動態滾動金幣、更新等級與經驗值條]
    
    UpdateStatsUI --> CheckLevelUp{經驗值是否達標升級?}
    CheckLevelUp -->|是| ShowLevelUp[前端全螢幕發送『LEVEL UP!』史詩金色字樣動畫]
    CheckLevelUp -->|否| RefreshList[更新任務清單狀態]
    ShowLevelUp --> RefreshList
    
    RefreshList --> End([完成本階段冒險主線])
```

---

## 2. 系統序列圖 (Sequence Diagram)

以「保單分析任務」的提交為例，展示瀏覽器、Flask Route、Python Models 與 SQLite 的通訊：

```mermaid
sequenceDiagram
    actor Adventurer as 冒險者
    participant Browser as 瀏覽器 (JS Fetch)
    participant FlaskRoute as Flask API (api.py)
    participant QuestModel as Quest Model (quest.py)
    participant AdvModel as Adventurer Model (adventurer.py)
    participant DB as SQLite 資料庫

    Adventurer->>Browser: 填寫保單分析表單並送出
    Browser->>FlaskRoute: POST /api/quests/2/submit (帶有 risk_level, coverage_amount 等 JSON 參數)
    
    activate FlaskRoute
    FlaskRoute->>FlaskRoute: 進行欄位基本驗證 (保額是否在範圍內)
    
    FlaskRoute->>QuestModel: 呼叫 get_quest_status(adventurer_id=1, quest_id=2)
    activate QuestModel
    QuestModel->>DB: SELECT status FROM adventurer_quests...
    DB-->>QuestModel: 回傳 status (應為 'active')
    deactivate QuestModel
    
    FlaskRoute->>QuestModel: 呼叫 complete_quest(adventurer_id=1, quest_id=2, form_data)
    activate QuestModel
    QuestModel->>DB: INSERT INTO quest_submissions (開戶或保單資料)
    QuestModel->>DB: UPDATE adventurer_quests SET status='completed', completed_at=...
    DB-->>QuestModel: 寫入成功
    QuestModel-->>FlaskRoute: 回傳 (True, 獎勵：250 Gold, 300 EXP)
    deactivate QuestModel
    
    FlaskRoute->>AdvModel: 呼叫 reward_adventurer(adventurer_id=1, gold=250, exp=300)
    activate AdvModel
    AdvModel->>DB: SELECT level, exp, gold FROM adventurers WHERE id=1
    DB-->>AdvModel: 回傳目前數值
    AdvModel->>AdvModel: 計算加成與升級邏輯 (溢出處理)
    AdvModel->>DB: UPDATE adventurers SET level=X, exp=Y, gold=Z WHERE id=1
    DB-->>AdvModel: 寫入成功
    AdvModel-->>FlaskRoute: 回傳最新角色狀態 (Level X, EXP Y, Gold Z, IsLevelUp=True)
    deactivate AdvModel

    FlaskRoute-->>Browser: 回傳 JSON: { success: true, new_stats: {...}, rewards: {...} }
    deactivate FlaskRoute
    
    Browser->>Browser: 觸發 Canvas 金色粒子特效與升級動畫
    Browser-->>Adventurer: 顯示「交付任務成功！金幣 +250，等級提升至 X！」
```

---

## 3. 功能路由對照表 (Route Reference)

| 功能描述 | HTTP 方法 | URL 路徑 | 請求參數 (JSON) | 回傳內容 |
| :--- | :--- | :--- | :--- | :--- |
| 取得冒險者資訊 | GET | `/api/adventurer` | 無 | 冒險者當前等級、經驗、金幣 |
| 取得主線任務列表 | GET | `/api/quests` | 無 | 任務列表與接取狀態、子目標進度 |
| 簽訂契約（接取任務） | POST | `/api/quests/<id>/accept` | 無 | 任務狀態變更為 'active' 成功訊息 |
| 提交開戶任務表單 | POST | `/api/quests/1/submit` | `real_name`, `character_class`, `vault_password`, `license_number` | 獎勵結算、更新後數值 |
| 提交保單分析表單 | POST | `/api/quests/2/submit` | `risk_level`, `coverage_amount`, `insurance_types` | 獎勵結算、更新後數值、解鎖狀態 |
