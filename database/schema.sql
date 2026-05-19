CREATE TABLE IF NOT EXISTS adventurers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    total_assets REAL DEFAULT 0,
    security_score REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS daily_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adventurer_id INTEGER NOT NULL,
    task_type TEXT NOT NULL,
    reference_id TEXT,
    reward_amount REAL NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(adventurer_id) REFERENCES adventurers(id)
);
