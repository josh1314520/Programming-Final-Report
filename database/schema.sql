CREATE TABLE IF NOT EXISTS adventurers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    total_assets REAL DEFAULT 0,
    security_score REAL DEFAULT 0
);
