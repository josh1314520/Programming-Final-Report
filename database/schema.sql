-- 冒險者金庫 - 守護靈裝備系統 資料表 Schema

-- 1. 玩家資源資料表 (單一玩家狀態，以 ID=1 代表當前登入玩家)
CREATE TABLE IF NOT EXISTS player (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gold INTEGER DEFAULT 50000,
    soul_stones INTEGER DEFAULT 50,
    last_daily TEXT NULL
);

-- 2. 守護靈資料表
CREATE TABLE IF NOT EXISTS guardians (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    element TEXT NOT NULL CHECK(element IN ('Fire', 'Water', 'Wind', 'Earth', 'Light', 'Shadow')),
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    base_hp INTEGER NOT NULL,
    base_atk INTEGER NOT NULL,
    base_def INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 3. 裝備資料表
CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('weapon', 'armor', 'accessory')),
    rarity TEXT NOT NULL CHECK(rarity IN ('Common', 'Rare', 'Epic', 'Legendary')),
    level INTEGER DEFAULT 1,
    hp_bonus INTEGER DEFAULT 0,
    atk_bonus INTEGER DEFAULT 0,
    def_bonus INTEGER DEFAULT 0,
    guardian_id INTEGER NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(guardian_id) REFERENCES guardians(id) ON DELETE SET NULL
);

-- 塞入初始測試種子資料 (如果表是空的)
-- 玩家
INSERT OR IGNORE INTO player (id, gold, soul_stones, last_daily) 
VALUES (1, 50000, 50, NULL);

-- 守護靈
INSERT INTO guardians (name, element, level, xp, base_hp, base_atk, base_def)
SELECT '烈焰鳳凰', 'Fire', 1, 0, 450, 85, 40
WHERE NOT EXISTS (SELECT 1 FROM guardians WHERE name = '烈焰鳳凰');

INSERT INTO guardians (name, element, level, xp, base_hp, base_atk, base_def)
SELECT '潮汐水靈', 'Water', 1, 0, 600, 55, 50
WHERE NOT EXISTS (SELECT 1 FROM guardians WHERE name = '潮汐水靈');

INSERT INTO guardians (name, element, level, xp, base_hp, base_atk, base_def)
SELECT '幽影白狼', 'Wind', 1, 0, 380, 95, 30
WHERE NOT EXISTS (SELECT 1 FROM guardians WHERE name = '幽影白狼');

INSERT INTO guardians (name, element, level, xp, base_hp, base_atk, base_def)
SELECT '大地泰坦', 'Earth', 1, 0, 800, 40, 80
WHERE NOT EXISTS (SELECT 1 FROM guardians WHERE name = '大地泰坦');

-- 裝備
INSERT INTO equipment (name, type, rarity, level, hp_bonus, atk_bonus, def_bonus, guardian_id)
SELECT '王者之劍', 'weapon', 'Legendary', 1, 150, 60, 0, 1
WHERE NOT EXISTS (SELECT 1 FROM equipment WHERE name = '王者之劍');

INSERT INTO equipment (name, type, rarity, level, hp_bonus, atk_bonus, def_bonus, guardian_id)
SELECT '熔岩重鎧', 'armor', 'Epic', 1, 300, 0, 40, 1
WHERE NOT EXISTS (SELECT 1 FROM equipment WHERE name = '熔岩重鎧');

INSERT INTO equipment (name, type, rarity, level, hp_bonus, atk_bonus, def_bonus, guardian_id)
SELECT '星光項鍊', 'accessory', 'Rare', 1, 100, 15, 10, 2
WHERE NOT EXISTS (SELECT 1 FROM equipment WHERE name = '星光項鍊');

INSERT INTO equipment (name, type, rarity, level, hp_bonus, atk_bonus, def_bonus, guardian_id)
SELECT '生鏽鐵劍', 'weapon', 'Common', 1, 20, 10, 0, NULL
WHERE NOT EXISTS (SELECT 1 FROM equipment WHERE name = '生鏽鐵劍');
