from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from ..models import User, Group
from ..forms import JoinGroupForm
from ..extensions import db
from .api import token_or_login_required

general_bp = Blueprint('general_bp', __name__)

@general_bp.route('/')
@token_or_login_required
def index():
    return redirect(url_for('general_bp.home'))

@general_bp.route('/home')
@token_or_login_required
def home():
    return render_template('index.html', name=current_user.username)

@general_bp.route('/before_request')
def before_request():
    if not current_user.is_authenticated and request.endpoint != 'auth_bp.auth_page':
        return redirect(url_for('auth_bp.auth_page'))

@general_bp.route('/join_group', methods=['GET', 'POST'])
@token_or_login_required
def join_group():
    form = JoinGroupForm()
    data = request.get_json() if request.is_json else request.form

    if form.validate_on_submit() or request.is_json:
        if current_user.passcode_attempts is None:
            current_user.passcode_attempts = 0 

        if current_user.passcode_attempts >= 10:
            response = {'message': 'Too many failed attempts. Please contact support.', 'status': 'danger'}
            return jsonify(response) if request.is_json else (flash(response['message'], response['status']), redirect(url_for('profile_bp.home')))

        try:
            group = Group.query.filter_by(passcode=data.get('passcode')).first()
            if not group:
                current_user.passcode_attempts += 1
                db.session.commit()
                response = {'message': 'Invalid passcode. Please try again.', 'status': 'danger'}
                return jsonify(response) if request.is_json else (flash(response['message'], response['status']), redirect(url_for('general_bp.join_group')))

            current_user.group = group
            current_user.passcode_attempts = 0  # Reset attempts on successful joining
            db.session.commit()
            response = {'message': 'You have successfully joined the group!', 'status': 'success'}
            return jsonify(response) if request.is_json else (flash(response['message'], response['status']), redirect(url_for('profile_bp.home')))

        except Exception as e:
            print("Failed to process request or insert to db")
            response = {'message': 'An error occurred. Please try again later.', 'status': 'danger'}
            return jsonify(response) if request.is_json else (flash(response['message'], response['status']), redirect(url_for('general_bp.join_group')))
    
    return render_template('join_group.html', title='Join Group', form=form)

@general_bp.route('/friends', methods=['GET'])
@token_or_login_required
def friends():
    if not current_user.group_id:
        response = {'message': 'You are not part of any group', 'users': [], 'no_friends': True}
        return jsonify(response) if request.is_json else render_template('friends.html', users=[], no_friends=True)

    users = User.query.filter(User.group_id == current_user.group_id).all()
    user_data = [
        {
            'id': user.id,
            'username': user.username,
            'profile_image': url_for('static', filename='profile_pics/' + (user.profile_image if user.profile_image else 'default.png'))
        }
        for user in users
    ]
    no_friends = len(users) == 0
    response = {'users': user_data, 'no_friends': no_friends}
    
    return jsonify(response) if request.is_json else render_template('friends.html', users=user_data, no_friends=no_friends)

@general_bp.route('/map', methods=['GET'])
@token_or_login_required
def map_view():
    return render_template('map.html')

@general_bp.route('/shows', methods=['GET'])
@token_or_login_required
def shows():
    return render_template('shows.html')

@general_bp.route('/my-shows', methods=['GET'])
@token_or_login_required
def my_shows():
    return render_template('my_shows.html')