from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from ..models import User, Group
from ..forms import JoinGroupForm
from ..extensions import db

general_bp = Blueprint('general_bp', __name__)

@general_bp.route('/')
@login_required
def index():
    return render_template('index.html', name=current_user.username)

@general_bp.route('/before_request')
def before_request():
    if not current_user.is_authenticated and request.endpoint != 'auth_bp.auth_page':
        return redirect(url_for('auth_bp.auth_page'))

@general_bp.route('/join_group', methods=['GET', 'POST'])
@login_required
def join_group():
    form = JoinGroupForm()
    if form.validate_on_submit():
        if current_user.passcode_attempts is None:
            current_user.passcode_attempts = 0  # Initialize passcode_attempts if it's None

        if current_user.passcode_attempts >= 10:
            flash('Too many failed attempts. Please contact support.', 'danger')
            return redirect(url_for('profile_bp.profile'))
        try:
            group = Group.query.filter_by(passcode=form.passcode.data).first()
            if not group:
                current_user.passcode_attempts += 1
                db.session.commit()
                flash('Invalid passcode. Please try again.', 'danger')
                return redirect(url_for('general_bp.join_group'))

            current_user.group = group
            current_user.passcode_attempts = 0  # Reset attempts on successful joining
            db.session.commit()
            flash('You have successfully joined the group!', 'success')
            return redirect(url_for('profile_bp.profile'))
        except Exception as e:
            print("Failed to process request or insert to db")
    return render_template('join_group.html', title='Join Group', form=form)

@general_bp.route('/friends', methods=['GET'])
@login_required
def friends():
    if not current_user.group_id:
        flash('You are not part of any group', 'warning')
        return render_template('friends.html', users=[], no_friends=True)

    users = User.query.filter(User.group_id == current_user.group_id).all()
    no_friends = len(users) == 0
    return render_template('friends.html', users=users, no_friends=no_friends)

@general_bp.route('/map', methods=['GET'])
@login_required
def map_view():
    return render_template('map.html')

@general_bp.route('/shows', methods=['GET'])
@login_required
def shows():
    return render_template('shows.html')
