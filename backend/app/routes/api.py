from flask import Blueprint, request, jsonify, current_app, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Api, Resource, fields
from flask_login import login_user, logout_user, current_user, login_required
from flask_jwt_extended import jwt_required, get_jwt_identity,decode_token,create_access_token, set_access_cookies
from functools import wraps
import jwt
import datetime
from ..models import User
from ..extensions import db
from datetime import datetime, timedelta


api_bp = Blueprint('api', __name__)
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(
    api_bp,
    version='1.0',
    title='Flask API with JWT-Based Authentication',
    description='Welcome to Shlaiman Finder App!',
    authorizations=authorizations
)

login_model = api.model('Login', {
    'email': fields.String(required=True, description='The email address'),
    'password': fields.String(required=True, description='The user password')
})

signup_model = api.model('Signup', {
    'email': fields.String(required=True, description='The email address'),
    'username': fields.String(required=True, description='The username'),
    'password': fields.String(required=True, description='The user password')
})

def token_or_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
        elif 'api_token' in request.cookies:
            token = request.cookies.get('api_token')

        if token:
            try:
                data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                user_id = data.get('sub')
                if not user_id:
                    raise jwt.InvalidTokenError
                
                user = User.query.get(user_id)
                if not user:
                    raise jwt.InvalidTokenError
                login_user(user)
            except jwt.ExpiredSignatureError:
                user = User.query.filter_by(api_token=token).first()
                if user:
                    new_token = generate_and_save_token(user)
                    response = redirect(url_for('profile_bp.profile'))
                    set_access_cookies(response, new_token)  # Set new JWT in cookie
                    return response
                else:
                    if request.is_json or request.path.startswith('/api/'):
                        return jsonify({'error': 'Token has expired'}), 401
                    else:
                        return redirect(url_for('auth_bp.auth_page'))
            except jwt.InvalidTokenError:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'error': 'Token is invalid'}), 401
                else:
                    return redirect(url_for('auth_bp.auth_page'))
        elif not current_user.is_authenticated:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Token is missing or invalid'}), 401
            else:
                return redirect(url_for('auth_bp.auth_page'))

        # Check if api_token is missing in the database
        if not current_user.api_token:
            new_token = generate_and_save_token(current_user)
            response = redirect(url_for('profile_bp.profile'))
            set_access_cookies(response, new_token)  # Set new JWT in cookie
            return response

        return f(*args, **kwargs)

    return decorated


def generate_and_save_token(user):
    # Check if the current token is valid
    if user.api_token:
        try:
            data = jwt.decode(user.api_token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            if data['exp'] > datetime.utcnow().timestamp():
                return user.api_token
        except jwt.ExpiredSignatureError:
            pass  
        except jwt.InvalidTokenError:
            pass  
    
    # Generate a new token
    token_data = {
        'user_id': user.id,
        'sub': user.id,
        'exp': (datetime.utcnow() + timedelta(days=3)).timestamp()
    }
    token = create_access_token(identity=user.id, additional_claims=token_data)
    user.api_token = token
    db.session.commit()
    return token

@api.route('/login')
class LoginResource(Resource):
    @api.expect(login_model)
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            api_token = user.generate_api_token(current_app.config['SECRET_KEY'])
            response = {
                'api_token': api_token,
                'msg': 'Successfully logged in!'
            }
            return response, 200
        else:
            return {'msg': 'Login failed. Check your email and password.'}, 401

@api.route('/signup')
class SignupResource(Resource):
    @api.expect(signup_model)
    def post(self):
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {"msg": "Email already in use. Please choose a different email."}, 409

        if len(password) < 6:
            return {"msg": "Password must be at least 6 characters long."}, 400

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        api_token = new_user.generate_api_token(current_app.config['SECRET_KEY'])
        response = {
            'api_token': api_token,
            'msg': 'Account created successfully!'
        }
        return response, 201

@api.route('/logout')
class LogoutResource(Resource):
    @api.doc(security='Bearer')
    @token_or_login_required
    def post(self, current_user):
        logout_user()
        return {'msg': 'Successfully logged out.'}, 200

@api.route('/protected')
class ProtectedResource(Resource):
    @api.doc(security='Bearer')
    @token_or_login_required
    def get(self, current_user):
        return {'msg': f'Hello, {current_user.username}! This is a protected route.'}, 200
    
@api.route('/validate')
class ValidateTokenResource(Resource):
    @api.doc(security='Bearer')
    @token_or_login_required
    def post(self, current_user):
        data = request.get_json()
        test_param = data.get('test')
        
        if test_param == 'true':
            return {'msg': 'Token is valid and test parameter is true'}, 200
        else:
            return {'msg': 'Token is valid, but test parameter is not true'}, 400
@api.route('/protected-endpoint')
class ProtectedEndpoint(Resource):
    @token_or_login_required
    def get(self, current_user):
        return jsonify({'msg': f'Hello, {current_user.username}'})
    
@api_bp.route('/test', methods=['GET'])
@jwt_required()
def test_api():
    user_id = get_jwt_identity()
    return jsonify({'msg': f'Hello, user {user_id}. Your token is valid!'}), 200

@api_bp.route('/validate_token', methods=['POST'])
@jwt_required()
def validate_token():
    user_id = get_jwt_identity()
    test_value = request.json.get('test', False)
    return jsonify({'msg': f'Token is valid for user {user_id} and test value is {test_value}'}), 200