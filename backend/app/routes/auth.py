from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from ..extensions import db, mail
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from ..forms import RequestResetForm
import smtplib
from datetime import datetime, timedelta
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity,create_access_token, set_access_cookies
)
from .api import token_or_login_required
import jwt

auth_bp = Blueprint('auth_bp', __name__)

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
        
        # Ensure the token is generated and saved
        token = generate_and_save_token(user)
        
        # Create a response object and set the token in the cookie
        response = redirect(url_for('profile_bp.profile'))
        response.set_cookie('api_token', token, httponly=True, secure=True)
        
        # If it's an API request, return the token in JSON format
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'api_token': token, 'user_id': user.id, 'msg': 'Successfully logged in!'})
        
        flash('Successfully logged in!', 'success')
        return response
    else:
        flash('Login failed. Check your email and password.', 'error')
        return redirect(url_for('auth_bp.auth_page'))
    
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() if request.is_json else request.form
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Email already in use. Please choose a different email.', 'error')
        return redirect(url_for('auth_bp.auth_page'))

    if len(password) < 6:
        flash('Password must be at least 6 characters long.', 'error')
        return redirect(url_for('auth_bp.auth_page'))

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(email=email, username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    #token = generate_and_save_token(new_user)
    access_token = create_access_token(identity=new_user.id)
    new_user.api_token = access_token
    db.session.commit()
    
    response = redirect(url_for('profile_bp.profile'))
    response.set_cookie('api_token', access_token, httponly=True, secure=True)
    flash('Account created successfully!', 'success')
    return response


#Test Tokens
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
    
@auth_bp.route('/logout')
@token_or_login_required
def logout():
    response = redirect(url_for('auth_bp.auth_page'))
    response.delete_cookie('api_token')
    logout_user()
    flash('You have been logged out.', 'success')
    return response


@auth_bp.route('/request_reset', methods=['GET', 'POST'])
def request_reset():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.get_user_by_email(email)
        if user:
            token = generate_reset_token(user.email)
            send_reset_email(user.email, token)
            flash('A password reset email has been sent.', 'info')
        else:
            flash('Email not found.', 'warning')
        return redirect(url_for('auth_bp.request_reset'))
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
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('auth_bp.request_reset'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth_bp.reset_password', token=token))
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('auth_bp.auth_page'))  
    
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