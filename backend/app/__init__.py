from flask import Flask, render_template
from flask_pymongo import PyMongo
from flask_login import LoginManager
from bson import ObjectId, errors  # Import ObjectId and errors
from .extensions import mongo, login_manager, mail
from datetime import timedelta
import os

mongo = PyMongo()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='')
    app.config['SECRET_KEY'] = 'zubur123'
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/shlaiman-mongo'
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

    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    mail.init_app(app)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.route('/')
    def home():
        return render_template('index.html')

    return app

@login_manager.user_loader
def load_user(user_id):
    try:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return User(user['email'], user['username'], user['password'], user['superuser'], user.get('group_id'), user.get('profile_image'))
    except errors.InvalidId:
        return None
    return None