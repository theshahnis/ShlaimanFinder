from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
import jwt
import datetime
from ..models import User
from ..extensions import db

api_bp = Blueprint('api_bp', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'error': 'Token is invalid or expired'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        api_token = user.generate_api_token(current_app.config['SECRET_KEY'])
        response = jsonify({
            'api_token': api_token,
            'msg': 'Successfully logged in!'
        })
        return response
    else:
        return jsonify({'msg': 'Login failed. Check your email and password.'}), 401

@api_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"msg": "Email already in use. Please choose a different email."}), 409

    if len(password) < 6:
        return jsonify({"msg": "Password must be at least 6 characters long."}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(email=email, username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    api_token = new_user.generate_api_token(current_app.config['SECRET_KEY'])
    response = jsonify({
        'api_token': api_token,
        'msg': 'Account created successfully!'
    })
    return response

@api_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    logout_user()
    return jsonify({'msg': 'Successfully logged out.'}), 200

@api_bp.route('/protected', methods=['GET'])
@token_required
def protected(current_user):
    return jsonify({'msg': f'Hello, {current_user.username}! This is a protected route.'}), 200
