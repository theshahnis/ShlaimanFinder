from flask import Blueprint, request, jsonify, current_app, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from ..models import User
from ..extensions import db, mail
from flask_mail import Message
import smtplib,jwt,os,datetime


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
        api_token = User.generate_api_token(user, os.getenv('JWT_SECRET_KEY'))
        user.api_token = api_token
        db.session.commit()  # Ensure the token is saved in the database

        response = jsonify({
            'api_token': api_token,
            'msg': 'Successfully logged in!',
            'location': url_for('profile_bp.profile')  # Include the redirect URL in the JSON response
        })
        response.set_cookie('api_token', api_token, httponly=True, secure=True)  # Set the token as a cookie
        return response
    else:
        return jsonify({'msg': 'Login failed. Check your email and password.'}), 401

# Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except Exception as e:
            return jsonify({'error': 'Token is invalid or expired', 'message': str(e)}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@auth_bp.route('/signup', methods=['POST'])
def signup():
    if request.content_type == 'application/json':
        data = request.get_json()
    else:
        data = request.form

    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({"msg": "Email, username, and password are required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"msg": "Email already in use. Please choose a different email."}), 409

    if len(password) < 6:
        return jsonify({"msg": "Password must be at least 6 characters long."}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(email=email, username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    api_token = new_user.generate_api_token(current_app.config['JWT_SECRET_KEY'])
    response = jsonify({
        'api_token': api_token,
        'msg': 'Account created successfully!',
    })
    response.headers['Location'] = url_for('profile_bp.profile')
    login_user(new_user)
    return response


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth_bp.auth_page'))


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


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        return jsonify({"msg": "Invalid or expired token."}), 400

    if request.method == 'POST':
        data = request.get_json()
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password != confirm_password:
            return jsonify({"msg": "Passwords do not match."}), 400
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
            db.session.commit()
            return jsonify({"msg": "Your password has been updated!"}), 200

    return render_template('reset_password.html', token=token)





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


@auth_bp.route('/generate_token', methods=['POST'])
@login_required
def generate_token():
    token = current_user.generate_api_token(current_app.config['JWT_SECRET_KEY'])
    return jsonify({'api_token': token})
