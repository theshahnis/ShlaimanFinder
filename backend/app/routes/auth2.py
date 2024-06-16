from flask import Blueprint, request, jsonify, current_app, redirect, url_for, flash,render_template
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
)
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from ..models import User
from ..extensions import db, mail
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
import smtplib
import datetime


auth_bp = Blueprint('auth_bp', __name__)

# JWT Configuration
jwt = JWTManager()

@auth_bp.route('/', methods=['GET', 'POST'])
def auth_page():
    if request.method == 'POST':
        if 'login' in request.form:
            return login()
        elif 'signup' in request.form:
            return signup()
    return render_template('auth.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() if request.is_json else request.form
    email = data.get('email')
    password = data.get('password')
    remember = True if data.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        login_user(user, remember=remember)
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)

        if request.is_json:
            return jsonify(access_token=access_token, refresh_token=refresh_token), 200
        else:
            flash('Successfully logged in!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('profile_bp.profile'))
    else:
        if request.is_json:
            return jsonify({"msg": "Bad email or password"}), 401
        else:
            flash('Login failed. Check your email and password.', 'error')
            return redirect(url_for('auth_bp.auth_page'))

def login_or_jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Try to verify JWT token
            verify_jwt_in_request()
            current_user_email = get_jwt_identity()
            # If JWT is valid, proceed
            return fn(*args, **kwargs)
        except NoAuthorizationError:
            # If JWT is not valid, fall back to session-based login
            if current_user.is_authenticated:
                return fn(*args, **kwargs)
            else:
                flash('You need to be logged in to access this page.', 'danger')
                return redirect(url_for('auth_bp.auth_page'))
    return wrapper

@auth_bp.route('/signup', methods=['POST'])
def signup():
    email = request.json.get('email')
    username = request.json.get('username')
    password = request.json.get('password')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"msg": "Email already in use. Please choose a different email."}), 409

    if len(password) < 6:
        return jsonify({"msg": "Password must be at least 6 characters long."}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(email=email, username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 201

@auth_bp.route('/logout_api', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    # Add jti to a revocation list (implement this in your app if needed)
    flash('You have been logged out.', 'success')
    return jsonify({"msg": "Successfully logged out"}), 200

@auth_bp.route('/logout')
@jwt_required()
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth_bp.auth_page'))


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@auth_bp.route('/request_reset', methods=['GET', 'POST'])
def request_reset():
    if request.method == 'POST':
        email = request.json.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user.email)
            send_reset_email(user.email, token)
            return jsonify({"msg": "A password reset email has been sent."}), 200
        return jsonify({"msg": "Email not found."}), 404
    return render_template('request_reset.html')

def send_reset_email(to, token_id):
    msg = Message('Shlaiman Finder - Password Reset Request', sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[to])
    msg.body = f'''To reset your password, visit the following link:
        {url_for('auth_bp.reset_password', token=token_id, _external=True)}
        If you did not make this request then simply ignore this email and no changes will be made.
        '''
    try:
        mail.send(msg)
        current_app.logger.info(f"Sent reset password to: {to}")
        return 'Email sent successfully!'
    except smtplib.SMTPException as e:
        current_app.logger.error(f"Failed to send email: {e}")
        return False

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        return jsonify({"msg": "Invalid or expired token."}), 400
    
    if request.method == 'POST':
        password = request.json.get('password')
        confirm_password = request.json.get('confirm_password')
        if password != confirm_password:
            return jsonify({"msg": "Passwords do not match."}), 400
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
            db.session.commit()
            return jsonify({"msg": "Your password has been updated!"}), 200  
    
    return render_template('reset_password.html', token=token)

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return None
    return email

@auth_bp.route('/test-email')
def test_email():
    msg = Message('Test Email', sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=['theshahnis@gmail.com'])
    msg.body = 'This is a test email sent from Flask-Mail with Postfix as the mail server.'
    try:
        mail.send(msg)
        return 'Email sent successfully!'
    except Exception as e:
        return f'Failed to send email: {e}'
    