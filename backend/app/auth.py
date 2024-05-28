from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .extensions import mongo, mail
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from bson import ObjectId, errors

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.get_user_by_email(email)
        if user and User.validate_login(user['password'], password):
            login_user(User(user['email'], user['username'], user['password'], user['superuser'], user.get('group_id'), user.get('profile_image')), remember=remember)
            flash('Successfully logged in!', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash('Login failed. Check your email and password.', 'error')
    return render_template('auth.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = User.get_user_by_email(email)
        if existing_user:
            flash('Email already in use. Please choose a different email.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
        else:
            user_id = User.create_user(email, username, password)
            login_user(User.get_user_by_id(user_id))
            flash('Account created successfully!', 'success')
            return redirect(url_for('main.profile'))
    return render_template('auth.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/request_reset', methods=['GET', 'POST'])
def request_reset():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.get_user_by_email(email)
        if user:
            token = generate_reset_token(user['email'])
            send_reset_email(user['email'], token)
            flash('A password reset email has been sent.', 'info')
        else:
            flash('Email not found.', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('request_reset.html')

def send_reset_email(to, token):
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[to])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_password', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('auth.request_reset'))
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.reset_password', token=token))
        user = User.get_user_by_email(email)
        if user:
            User.update_user(user['_id'], {'password': password})
            flash('Your password has been updated!', 'success')
            return redirect(url_for('auth.login'))
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
