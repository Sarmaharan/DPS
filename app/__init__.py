"""DPS - AI-Based Diabetes Prediction & Patient Management System."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """Create and configure the Flask application."""
    from config import Config
    import os
    
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(id):
        from app.models import User
        return User.query.get(int(id))
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.patient_routes import patient_bp
    from app.routes.prediction_routes import prediction_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.report_routes import report_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(patient_bp, url_prefix='/patients')
    app.register_blueprint(prediction_bp, url_prefix='/prediction')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(report_bp, url_prefix='/reports')
    
    with app.app_context():
        db.create_all()
        from app.routes.auth_routes import init_default_users
        init_default_users()
        
        # Train ML models on startup
        try:
            from app.ml_engine import MLEngine
            MLEngine.train_models()
        except Exception as e:
            print(f"ML engine initialization: {e}")
    
    @app.route('/')
    def index():
        from flask import redirect, url_for
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.overview'))
        return redirect(url_for('auth.login'))
    
    return app
