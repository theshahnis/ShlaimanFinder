from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from .extensions import db, login_manager, mail, migrate
from datetime import timedelta
import os

class Base(DeclarativeBase):
  pass

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='')
    app.config['SECRET_KEY'] = 'zubur123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shlaimanSQL.db'
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=180)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/profile_pics')

    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'agileprocessuser@gmail.com'
    app.config['MAIL_PASSWORD'] = 'qqgs uegs bgvg wfbh '
    app.config['SECURITY_PASSWORD_SALT'] = '9145f66020c06c5dfcdeaa017d5ff82f'

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    mail.init_app(app)
    migrate.init_app(app, db)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/')

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.route('/')
    def index():
        return app.send_static_file('auth.html')

    with app.app_context():
        db.create_all()

    context = ('cert.pem', 'key.pem')  # Paths to your certificate and key files
    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))