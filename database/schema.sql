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
