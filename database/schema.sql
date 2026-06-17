-- ==========================================
-- 冒險者金庫 統一資料庫 Schema 與初始資料
-- ==========================================

-- 啟用外鍵約束
PRAGMA foreign_keys = ON;

-- ------------------------------------------
-- 1. 清理舊資料表 (重置用，順序需符合外鍵相依性)
-- ------------------------------------------
DROP TABLE IF EXISTS quest_submissions;
DROP TABLE IF EXISTS adventurer_quests;
DROP TABLE IF EXISTS quest_objectives;
DROP TABLE IF EXISTS quests;
DROP TABLE IF EXISTS adventurers;
DROP TABLE IF EXISTS guardians;
DROP TABLE IF EXISTS vault_status;
DROP TABLE IF EXISTS stress_test_reports;
DROP TABLE IF EXISTS daily_tasks;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS guardian;
DROP TABLE IF EXISTS investments;
DROP TABLE IF EXISTS users;

-- ------------------------------------------
-- 2. 建立主要資料表
-- ------------------------------------------

-- 2.1 冒險者角色表 (Quest System)
CREATE TABLE adventurers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    level INTEGER NOT NULL DEFAULT 1,
    exp INTEGER NOT NULL DEFAULT 0,
    gold INTEGER NOT NULL DEFAULT 500,
    title TEXT NOT NULL DEFAULT '見習冒險者',
    total_assets REAL DEFAULT 10000.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2.2 任務定義表
CREATE TABLE quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    story_intro TEXT NOT NULL,
    reward_gold INTEGER NOT NULL DEFAULT 0,
    reward_exp INTEGER NOT NULL DEFAULT 0,
    prerequisite_quest_id INTEGER,
    display_order INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (prerequisite_quest_id) REFERENCES quests(id) ON DELETE SET NULL
);

-- 2.3 任務子目標定義表
CREATE TABLE quest_objectives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quest_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    code_identifier TEXT NOT NULL,
    FOREIGN KEY (quest_id) REFERENCES quests(id) ON DELETE CASCADE
);

-- 2.4 冒險者任務接取進度表 (多對多)
CREATE TABLE adventurer_quests (
    adventurer_id INTEGER NOT NULL,
    quest_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'locked', -- locked / available / active / completed
    accepted_at DATETIME,
    completed_at DATETIME,
    PRIMARY KEY (adventurer_id, quest_id),
    FOREIGN KEY (adventurer_id) REFERENCES adventurers(id) ON DELETE CASCADE,
    FOREIGN KEY (quest_id) REFERENCES quests(id) ON DELETE CASCADE
);

-- 2.5 任務表單提交歷史表
CREATE TABLE quest_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adventurer_id INTEGER NOT NULL,
    quest_id INTEGER NOT NULL,
    submitted_data TEXT NOT NULL, -- 儲存 JSON 格式的表單資料
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (adventurer_id) REFERENCES adventurers(id) ON DELETE CASCADE,
    FOREIGN KEY (quest_id) REFERENCES quests(id) ON DELETE CASCADE
);

-- 2.6 守護靈狀態表 (吳秉洋模組)
CREATE TABLE guardians (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    asset_value REAL DEFAULT 0,
    risk_tolerance TEXT DEFAULT 'balanced', -- conservative, balanced, aggressive
    stage INTEGER DEFAULT 1,
    color TEXT DEFAULT 'Green',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2.7 金庫實體物資狀態表 (高叡廷/模擬器模組)
CREATE TABLE vault_status (
    id INTEGER PRIMARY KEY,
    gold INTEGER NOT NULL DEFAULT 5000,
    mana_crystals INTEGER NOT NULL DEFAULT 2000,
    bonds INTEGER NOT NULL DEFAULT 2000,
    dragon_eggs INTEGER NOT NULL DEFAULT 500,
    supplies INTEGER NOT NULL DEFAULT 500
);

-- 2.8 歷史壓力測試報告表 (模擬器模組)
CREATE TABLE stress_test_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    disaster_type TEXT NOT NULL,
    portfolio_distribution TEXT NOT NULL, -- JSON String
    hedging_upgrades TEXT NOT NULL,        -- JSON String
    max_drawdown REAL NOT NULL,
    recovery_period INTEGER NOT NULL,
    initial_total_val REAL NOT NULL,
    min_total_val REAL NOT NULL,
    final_total_val REAL NOT NULL,
    hedging_advice TEXT NOT NULL,
    chart_data TEXT NOT NULL               -- JSON String
);

-- 2.9 每日閱讀新聞任務表 (陳宇睿模組)
CREATE TABLE daily_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adventurer_id INTEGER NOT NULL,
    task_type TEXT NOT NULL, -- 'read_news'
    reference_id TEXT, -- news url
    reward_amount INTEGER NOT NULL DEFAULT 50,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------
-- 3. 跨模組相容與模擬資料表 (與 A/C 同學之部分代碼相容)
-- ------------------------------------------

-- 3.1 模擬用戶表
CREATE TABLE users (
    student_id TEXT PRIMARY KEY,
    gold INTEGER DEFAULT 0,
    exp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1
);

-- 3.2 模擬守護靈表 (包含 defense, insurance_score, insurance_armor 欄位)
CREATE TABLE guardian (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    stage INTEGER DEFAULT 1,
    color TEXT DEFAULT 'Green',
    defense INTEGER DEFAULT 0,
    insurance_score INTEGER DEFAULT 50,
    insurance_armor REAL DEFAULT 0.0,
    FOREIGN KEY (student_id) REFERENCES users (student_id) ON DELETE CASCADE
);

-- 3.3 模擬任務進度表
CREATE TABLE tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    main_status TEXT DEFAULT 'pending',
    news_completed_at DATETIME,
    FOREIGN KEY (student_id) REFERENCES users (student_id) ON DELETE CASCADE
);

-- 3.4 模擬投資持股表 (包含 stock_value, cash, stock_quantity, current_price 等欄位)
CREATE TABLE investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    stock_code TEXT NOT NULL,
    shares_held INTEGER DEFAULT 0,
    average_cost REAL DEFAULT 0.0,
    stock_value REAL DEFAULT 0.0,
    cash REAL DEFAULT 10000.0,
    stock_quantity REAL DEFAULT 0.0,
    current_price REAL DEFAULT 0.0,
    FOREIGN KEY (student_id) REFERENCES users (student_id) ON DELETE CASCADE
);

-- ------------------------------------------
-- 4. 寫入初始測試資料
-- ------------------------------------------

-- 4.1 預設冒險者玩家 (Hero)
INSERT INTO adventurers (id, username, level, exp, gold, title, total_assets)
VALUES (1, 'Hero', 1, 0, 500, '見習冒險者', 10000.0);

-- 4.2 預設用戶
INSERT INTO users (student_id, gold, exp, level)
VALUES ('D1490050', 500, 0, 1);
INSERT INTO users (student_id, gold, exp, level)
VALUES ('1', 500, 0, 1);

-- 4.3 預設守護靈裝備 (guardian)
INSERT INTO guardian (id, student_id, stage, color, defense, insurance_score, insurance_armor)
VALUES (1, 'D1490050', 1, 'Green', 0, 75, 75.0);
INSERT INTO guardian (id, student_id, stage, color, defense, insurance_score, insurance_armor)
VALUES (2, '1', 1, 'Green', 0, 50, 50.0);

-- 4.4 預設守護靈狀態 (guardians)
INSERT INTO guardians (id, user_id, asset_value, risk_tolerance, stage, color)
VALUES (1, 1, 10000.0, 'balanced', 1, '#50E3C2');

-- 4.5 預設股市持股 (investments)
INSERT INTO investments (id, student_id, stock_code, shares_held, average_cost, stock_value, cash, stock_quantity, current_price)
VALUES (1, 'D1490050', '2330.TW', 10, 1500.0, 15000.0, 10000.0, 10.0, 1500.0);
INSERT INTO investments (id, student_id, stock_code, shares_held, average_cost, stock_value, cash, stock_quantity, current_price)
VALUES (2, '1', '2330.TW', 10, 1500.0, 15000.0, 10000.0, 10.0, 1500.0);

-- 4.6 預設主線任務
INSERT INTO quests (id, title, description, story_intro, reward_gold, reward_exp, prerequisite_quest_id, display_order)
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

INSERT INTO quests (id, title, description, story_intro, reward_gold, reward_exp, prerequisite_quest_id, display_order)
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

-- 4.7 任務子目標
INSERT INTO quest_objectives (id, quest_id, description, code_identifier) VALUES 
(1, 1, '登記您的冒險者真實姓名 (填寫冒險者真名，至少 2 字)', 'real_name'),
(2, 1, '選擇您的守護冒險職業 (下拉選擇職業)', 'character_class'),
(3, 1, '設定六位數以上的金庫密碼 (填寫安全密碼，至少 6 字)', 'vault_password'),
(4, 1, '輸入您的冒險執照編號 (格式: ADV-XXXXX)', 'license_number');

INSERT INTO quest_objectives (id, quest_id, description, code_identifier) VALUES 
(5, 2, '評估當前探險風險等級 (單選風險級別)', 'risk_level'),
(6, 2, '設定期望之保險保障額度 (10,000 ~ 1,000,000 金幣)', 'coverage_amount'),
(7, 2, '勾選主要投保類型 (可複選投保項目)', 'insurance_types');

-- 4.8 冒險者初始任務狀態
INSERT INTO adventurer_quests (adventurer_id, quest_id, status)
VALUES (1, 1, 'available');

INSERT INTO adventurer_quests (adventurer_id, quest_id, status)
VALUES (1, 2, 'locked');

-- 4.9 金庫初始狀態
INSERT INTO vault_status (id, gold, mana_crystals, bonds, dragon_eggs, supplies)
VALUES (1, 5000, 2000, 2000, 500, 500);

-- 4.10 預設壓力測試歷史報告
INSERT INTO stress_test_reports (
    id, disaster_type, portfolio_distribution, hedging_upgrades, 
    max_drawdown, recovery_period, initial_total_val, 
    min_total_val, final_total_val, hedging_advice, chart_data
) VALUES (
    1,
    '2008 年矮人銀行金融海嘯',
    '{"gold": 10, "mana_crystals": 40, "bonds": 20, "dragon_eggs": 20, "supplies": 10}',
    '[]',
    46.85,
    24,
    10000.0,
    5315.0,
    6850.0,
    '您的投資組合中，「魔力水晶」與「飛龍蛋」佔比高達 60%。在此次矮人銀行信用崩潰中，高風險板塊全面失血，且因為沒有購買「公會存託保險」，導致皇家公債的部分也蒙受了無效對沖。建議大幅提升「實體黃金」以作為熊市避難所，並配置至少 20% 黃金對沖合約。',
    '[{"month": 0, "value": 10000.0}, {"month": 1, "value": 9000.0}, {"month": 2, "value": 8200.0}, {"month": 3, "value": 7500.0}, {"month": 4, "value": 7000.0}, {"month": 5, "value": 6500.0}, {"month": 6, "value": 6000.0}, {"month": 7, "value": 5500.0}, {"month": 8, "value": 5315.0}, {"month": 9, "value": 5400.0}, {"month": 10, "value": 5500.0}, {"month": 11, "value": 5600.0}, {"month": 12, "value": 5700.0}, {"month": 13, "value": 5800.0}, {"month": 14, "value": 5900.0}, {"month": 15, "value": 6000.0}, {"month": 16, "value": 6100.0}, {"month": 17, "value": 6200.0}, {"month": 18, "value": 6300.0}, {"month": 19, "value": 6400.0}, {"month": 20, "value": 6500.0}, {"month": 21, "value": 6600.0}, {"month": 22, "value": 6700.0}, {"month": 23, "value": 6800.0}, {"month": 24, "value": 6850.0}]'
);

INSERT INTO stress_test_reports (
    id, disaster_type, portfolio_distribution, hedging_upgrades, 
    max_drawdown, recovery_period, initial_total_val, 
    min_total_val, final_total_val, hedging_advice, chart_data
) VALUES (
    2,
    '2020 年魔力瘟疫疫情大爆發',
    '{"gold": 40, "mana_crystals": 10, "bonds": 20, "dragon_eggs": 5, "supplies": 25}',
    '["強化冷鏈糧倉"]',
    14.26,
    7,
    10000.0,
    8574.0,
    11850.0,
    '非常出色的防禦布局！您配置了高達 40% 的實體黃金以抵禦大盤崩盤，且在「強化冷鏈糧倉」的加持下，您的糧食儲備在第 4 個月價格飛漲時為您帶來了豐厚的利潤。這完美抵銷了魔力水晶在疫情初期的跌幅。繼續保持此類平衡防禦配置！',
    '[{"month": 0, "value": 10000.0}, {"month": 1, "value": 9700.0}, {"month": 2, "value": 9400.0}, {"month": 3, "value": 8574.0}, {"month": 4, "value": 8800.0}, {"month": 5, "value": 9100.0}, {"month": 6, "value": 9400.0}, {"month": 7, "value": 10000.0}, {"month": 8, "value": 10200.0}, {"month": 9, "value": 10400.0}, {"month": 10, "value": 10600.0}, {"month": 11, "value": 10800.0}, {"month": 12, "value": 11000.0}, {"month": 13, "value": 11100.0}, {"month": 14, "value": 11200.0}, {"month": 15, "value": 11300.0}, {"month": 16, "value": 11400.0}, {"month": 17, "value": 11500.0}, {"month": 18, "value": 11600.0}, {"month": 19, "value": 11700.0}, {"month": 20, "value": 11750.0}, {"month": 21, "value": 11800.0}, {"month": 22, "value": 11820.0}, {"month": 23, "value": 11840.0}, {"month": 24, "value": 11850.0}]'
);
