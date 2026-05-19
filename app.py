import sqlite3
from flask import Flask
from app.routes.dashboard import dashboard_bp
import os

def create_app():
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    app.config['SECRET_KEY'] = 'dev_secret_key'
    app.config['DATABASE'] = os.path.join(app.instance_path, 'database.db')

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register blueprints
    app.register_blueprint(dashboard_bp)

    return app

app = create_app()

def init_db():
    db_path = app.config['DATABASE']
    with sqlite3.connect(db_path) as conn:
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        
        # Insert a default adventurer if none exists
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM adventurers")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO adventurers (name, total_assets, security_score) VALUES (?, ?, ?)",
                           ('預設勇者', 5000, 30))
            conn.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
