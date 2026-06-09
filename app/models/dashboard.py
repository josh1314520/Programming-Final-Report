import sqlite3
from flask import current_app

def get_db_connection():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def get_adventurer(adventurer_id):
    try:
        conn = get_db_connection()
        adventurer = conn.execute('SELECT * FROM adventurers WHERE id = ?', (adventurer_id,)).fetchone()
        conn.close()
        return adventurer
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
