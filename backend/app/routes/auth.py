from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from ..extensions import db, mail
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from ..forms import RequestResetForm
import smtplib, jwt



auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
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
        return redirect(url_for('profile_bp.profile'))
    else:
        flash('Login failed. Check your email and password.', 'error')
        return redirect(url_for('auth_bp.auth_page'))
    

def signup():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

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
    flash('Account created successfully!', 'success')
    return redirect(url_for('profile_bp.profile'))

@auth_bp.route('/logout')
@token_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth_bp.auth_page'))


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
    

# New json logic
@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid email or password'}), 401
    

@auth_bp.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({'error': 'Email, password and username are required'}), 400
    

@auth_bp.route('/api/logout', methods=['POST'])
@token_required
def api_logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already in use. Please choose a different email.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long.'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(email=email, username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)

    return jsonify({'message': 'Account created successfully!', 'user_id': new_user.id}), 201

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
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)

    return decorated