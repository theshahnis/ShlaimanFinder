from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from app.extensions import db, login_manager, mail, migrate
from datetime import timedelta
import os
from dotenv import load_dotenv
from app.routes import register_blueprints


class Base(DeclarativeBase):
  pass

def create_app():
    load_dotenv()

    app = Flask(__name__, static_folder='static', static_url_path='')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=180)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/profile_pics')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your_email@gmail.com')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your_password')
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT', 'default_salt')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.auth_page'
    mail.init_app(app)
    migrate.init_app(app, db)

    register_blueprints(app)

    @app.route('/')
    def index():
        return app.send_static_file('auth.html')

    context = (os.getenv('SSL_CERT_PATH', 'cert.pem'), os.getenv('SSL_KEY_PATH', 'key.pem'))
    return app

    # with app.app_context():
    #     db.create_all()

    

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))