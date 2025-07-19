from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
babel = Babel()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bitte melden Sie sich an, um auf diese Seite zuzugreifen.'
    login_manager.login_message_category = 'info'
    
    # Configure Flask-Babel
    app.config['LANGUAGES'] = ['en', 'de']
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
    
    def get_locale():
        # 1. Check URL parameter
        requested_lang = request.args.get('lang')
        if requested_lang in app.config['LANGUAGES']:
            session['language'] = requested_lang
            return requested_lang
        
        # 2. Check session
        if 'language' in session and session['language'] in app.config['LANGUAGES']:
            return session['language']
        
        # 3. Fall back to browser preference or default
        return request.accept_languages.best_match(app.config['LANGUAGES']) or app.config['BABEL_DEFAULT_LOCALE']
    
    babel.init_app(app, locale_selector=get_locale)
    
    # Make get_locale available in templates
    @app.context_processor
    def inject_conf_vars():
        return {
            'get_locale': get_locale
        }
    
    # User loader function
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Create upload directories if they don't exist
    os.makedirs(app.config['PDF_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['IMAGE_UPLOAD_FOLDER'], exist_ok=True)
    
    # Import models to ensure they're registered with SQLAlchemy
    from app.models import User, Post, Image, RegistrationToken
    
    
    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    return app