from flask import Flask
from app.routes.api import api_bp

def create_app():
    app = Flask(__name__)
    
    # 註冊 Blueprint
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        return "Welcome to Adventurer's Vault API"
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
