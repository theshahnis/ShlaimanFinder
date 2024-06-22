from flask import Flask, render_template, redirect, request, jsonify, flash,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from app.extensions import db, login_manager, mail, migrate
from datetime import timedelta
import os,logging
from dotenv import load_dotenv
from app.routes import register_blueprints 
from flask_jwt_extended import JWTManager,create_access_token, create_refresh_token, jwt_required, get_jwt_identity



api = Api(version='1.0', title='Shlaiman Finder API', description='A simple API', doc='/docs')

class Base(DeclarativeBase):
  pass

def create_app():
    load_dotenv()

    app = Flask(__name__, static_folder='static', static_url_path='')
    

    

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10080)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/profile_pics')
    #app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024    
    app.config['MAIL_SERVER'] = 'localhost'
    app.config['MAIL_PORT'] = 25
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = None
    app.config['MAIL_PASSWORD'] = None
    app.config['MAIL_DEFAULT_SENDER'] = 'Shlaiman Finder <agileprocessuser@gmail.com>'
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SOUND_UPLOAD_FOLDER'] = 'static/sounds'
    app.config['TWILIO_ACCOUNT_SID'] = os.getenv('TWILIO_ACCOUNT_SID')
    app.config['TWILIO_AUTH_TOKEN'] = os.getenv('TWILIO_AUTH_TOKEN')
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.auth_page'
    mail.init_app(app)
    migrate.init_app(app, db)
    
    jwt = JWTManager(app) 


    register_blueprints(app)

    api.init_app(app)

    from app.routes.api import api as api_namespace
    from app.routes.profile import profile_ns
    from app.routes.show import show_ns
    from app.routes.superuser import superuser_ns

    api.add_namespace(api_namespace, path='/api/v1')
    api.add_namespace(profile_ns, path='/profile')
    api.add_namespace(show_ns, path='/show')
    #api.add_namespace(superuser_ns, path='/superuser')

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('profile_bp.profile'))
        else:
            return redirect(url_for('auth_bp.auth_page'))
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        flash('File is too large. Maximum file size is 32 MB.', 'danger')
        return redirect(request.url)

    context = (os.getenv('SSL_CERT_PATH', 'cert.pem'), os.getenv('SSL_KEY_PATH', 'key.pem'))

    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler('error.log', maxBytes=10240, backupCount=10)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('ShlaimanFinder startup')



    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))


