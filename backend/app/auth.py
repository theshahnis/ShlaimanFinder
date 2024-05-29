from flask import Blueprint, render_template, redirect, url_for, request, flash,current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .extensions import db, mail
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message


auth = Blueprint('auth', __name__)

@auth.route('/auth', methods=['GET', 'POST'])
def auth_page():
    if request.method == 'POST':
        if 'login' in request.form:
            return login()
        elif 'signup' in request.form:
            return signup()
    return render_template('auth.html')

def login():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user, remember=remember)
        flash('Successfully logged in!', 'success')
        return redirect(url_for('main.profile'))
    else:
        flash('Login failed. Check your email and password.', 'error')
        return redirect(url_for('auth.auth_page'))

def signup():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Email already in use. Please choose a different email.', 'error')
        return redirect(url_for('auth.auth_page'))

    if len(password) < 6:
        flash('Password must be at least 6 characters long.', 'error')
        return redirect(url_for('auth.auth_page'))

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(email=email, username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    flash('Account created successfully!', 'success')
    return redirect(url_for('main.profile'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.auth_page'))


@auth.route('/request_reset', methods=['GET', 'POST'])
def request_reset():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user.email)
            send_reset_email(user.email, token)
            flash('A password reset email has been sent.', 'info')
        else:
            flash('Email not found.', 'warning')
        return redirect(url_for('auth.auth_page'))
    return render_template('request_reset.html')

def send_reset_email(to, token):
    msg = Message('Shlaiman Finder-Password Reset Request', sender='Shlaiman@gmail.com', recipients=[to])
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
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('auth.auth_page'))
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