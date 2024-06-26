#from .auth import auth_bp as auth_blueprint
from .auth import auth_bp as auth_blueprint
from .profile import profile_bp as profile_blueprint
from .superuser import superuser_bp as superuser_blueprint
from .location import location_bp as location_blueprint
from .show import show_bp as show_blueprint
from .general import general_bp as general_blueprint
from .map import map_bp as map_blueprint
from .api import api_bp as api_blueprint
from .soundboard import soundboard_bp as soundboard_blueprint
from .sos import sos_bp
from .home import home_bp

def register_blueprints(app):
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    #app.register_blueprint(auth2_blueprint, name='api_auth', url_prefix='/auth2')
    app.register_blueprint(profile_blueprint, url_prefix='/profile')
    app.register_blueprint(superuser_blueprint, url_prefix='/superuser')
    app.register_blueprint(location_blueprint, url_prefix='/location')
    app.register_blueprint(show_blueprint, url_prefix='/show')
    app.register_blueprint(general_blueprint, url_prefix='/')
    app.register_blueprint(map_blueprint, url_prefix='/map')
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    app.register_blueprint(soundboard_blueprint, url_prefix='/soundboard')
    app.register_blueprint(sos_bp, url_prefix='/sos')
    app.register_blueprint(home_bp, url_prefix='/home')
