from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from routes.births import births_bp
from routes.deaths import deaths_bp
from routes.analytics import analytics_bp
from routes.anomalies import anomalies_bp
from routes.reports import reports_bp
from routes.users import users_bp
from auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)
    
    db.init_app(app)
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(births_bp, url_prefix='/api')
    app.register_blueprint(deaths_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(anomalies_bp, url_prefix='/api')
    app.register_blueprint(reports_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
    