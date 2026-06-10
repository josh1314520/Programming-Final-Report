DROP TABLE IF EXISTS guardians;

CREATE TABLE guardians (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    asset_value REAL DEFAULT 0,
    risk_tolerance TEXT DEFAULT 'balanced', -- conservative, balanced, aggressive
    stage INTEGER DEFAULT 1,
    color TEXT DEFAULT 'Green',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 寫入初始測試資料
-- ==========================================

-- 1. 插入預設冒險者玩家 (Hero)
INSERT OR IGNORE INTO adventurers (id, username, level, exp, gold, title)
VALUES (1, 'Hero', 1, 0, 500, '見習冒險者');

-- 2. 插入預設主線任務
-- 主線一：開戶任務 (契約之印)
INSERT OR IGNORE INTO quests (id, title, description, story_intro, reward_gold, reward_exp, prerequisite_quest_id, display_order)
VALUES (
    1, 
    '契約之印 (開戶任務)', 
    '與冒險者公會簽訂神聖的黃金契約，開啟個人專屬的冒險者金庫保險箱。', 
    '新手冒險者，歡迎來到金庫公會。在這裡，唯有刻下『契約之印』，你的財富才能受到魔法結界的終身庇護。請簽下你的真名與抉擇！', 
    100, 
    150, 
    NULL, 
    1
);

-- 主線二：保單分析任務 (命運之御)
INSERT OR IGNORE INTO quests (id, title, description, story_intro, reward_gold, reward_exp, prerequisite_quest_id, display_order)
VALUES (
    2, 
    '命運之御 (保單分析任務)', 
    '分析人身與裝備意外防護保單，在涉足高風險地下城前做好全方位保險規劃。', 
    '契約已成，金庫已啟。然而，生死無常，巨龍吐息與陷阱暗箭隨處可見。冒險者，在踏入黑暗前，公會法師需要評估你的『命運之御』防護保險，確保即便靈魂消散，你的金庫遺產亦能妥善處置！', 
    250, 
    300, 
    1, 
    2
);

-- 3. 插入任務子目標
-- 開戶任務的 4 個目標
INSERT OR IGNORE INTO quest_objectives (id, quest_id, description, code_identifier) VALUES 
(1, 1, '登記您的冒險者真實姓名 (填寫冒險者真名，至少 2 字)', 'real_name'),
(2, 1, '選擇您的守護冒險職業 (下拉選擇職業)', 'character_class'),
(3, 1, '設定六位數以上的金庫密碼 (填寫安全密碼，至少 6 字)', 'vault_password'),
(4, 1, '輸入您的冒險執照編號 (格式: ADV-XXXXX)', 'license_number');

-- 保單分析任務的 3 個目標
INSERT OR IGNORE INTO quest_objectives (id, quest_id, description, code_identifier) VALUES 
(5, 2, '評估當前探險風險等級 (單選風險級別)', 'risk_level'),
(6, 2, '設定期望之保險保障額度 (10,000 ~ 1,000,000 金幣)', 'coverage_amount'),
(7, 2, '勾選主要投保類型 (可複選投保項目)', 'insurance_types');

-- 4. 插入冒險者初始任務狀態
-- 任務一為 available (可接取)，任務二為 locked (鎖定)
INSERT OR IGNORE INTO adventurer_quests (adventurer_id, quest_id, status)
VALUES (1, 1, 'available');

INSERT OR IGNORE INTO adventurer_quests (adventurer_id, quest_id, status)
VALUES (1, 2, 'locked');
