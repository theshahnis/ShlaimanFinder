import os
import secrets
from flask import current_app, Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from .models import User, Group,Location
from .extensions import db
from .forms import UpdateProfileForm, JoinGroupForm
from datetime import datetime
from pytz import timezone

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('index.html', name=current_user.username)

@main.before_request
def before_request():
    if not current_user.is_authenticated and request.endpoint != 'auth.auth_page':
        return redirect(url_for('auth.auth_page'))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        try:
            if form.profile_image.data:
                picture_file = save_picture(form.profile_image.data)
                current_user.profile_image = picture_file
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your account has been updated!', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            db.session.rollback()
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image) if current_user.profile_image else None
    return render_template('profile.html', title='Profile', form=form, profile_image=profile_image)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@main.route('/superuser')
@login_required
def superuser():
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('main.profile'))
    users = User.query.all()
    groups = Group.query.all()  # Add this line to fetch groups
    return render_template('superuser.html', users=users, groups=groups)

@main.route('/superuser/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('main.profile'))

    user = User.query.get_or_404(user_id)
    groups = Group.query.all()

    if request.method == 'POST':
        user.email = request.form['email']
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        group_id = request.form['group_id']
        if group_id:
            user.group_id = int(group_id)
        else:
            user.group_id = None
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('main.superuser'))

    return render_template('edit_user.html', user=user, groups=groups)

@main.route('/superuser/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('main.profile'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('main.superuser'))

@main.route('/superuser/add_group', methods=['POST'])
@login_required
def add_group():
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('main.profile'))
    group_name = request.form['group_name']
    passcode = request.form['passcode']
    new_group = Group(name=group_name, passcode=passcode)
    db.session.add(new_group)
    db.session.commit()
    flash('Group added successfully', 'success')
    return redirect(url_for('main.superuser'))

@main.route('/location', methods=['GET'])
@login_required
def location():
    return render_template('location.html')

@main.route('/location', methods=['POST'])
@login_required
def update_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    print(f"lati:{latitude} , long:{longitude}")
    if latitude and longitude:
        # Fetch the latest location entry for the user
        location = Location.query.filter_by(user_id=current_user.id).order_by(Location.timestamp.desc()).first()
        if location:
            # Update the existing entry
            location.latitude = latitude
            location.longitude = longitude
            location.timestamp = datetime.now()
        else:
            # Create a new location entry if none exists
            location = Location(user_id=current_user.id, latitude=latitude, longitude=longitude, timestamp=datetime.now(timezone('Etc/GMT+3')))
            db.session.add(location)

        db.session.commit()
        return jsonify({'message': 'Location updated successfully'}), 200
    return jsonify({'message': 'Invalid data'}), 400


@main.route('/location/data', methods=['GET'])
@login_required
def get_location_data():
    location = Location.query.filter_by(user_id=current_user.id).order_by(Location.timestamp.desc()).first()
    if location:
        return jsonify({
            'latitude': location.latitude,
            'longitude': location.longitude,
            'timestamp': location.timestamp.isoformat()
        }), 200
    return jsonify({'message': 'No location data found'}), 404

@main.route('/location/<int:user_id>', methods=['GET'])
@login_required
def get_user_location(user_id):
    location = Location.query.filter_by(user_id=user_id).order_by(Location.timestamp.desc()).first()
    if location:
        return jsonify({
            'latitude': location.latitude,
            'longitude': location.longitude,
            'timestamp': location.timestamp.isoformat()
        }), 200
    return jsonify({'message': 'No location data found'}), 404


@main.route('/join_group', methods=['GET', 'POST'])
@login_required
def join_group():
    form = JoinGroupForm()
    if form.validate_on_submit():
        if current_user.passcode_attempts is None:
            current_user.passcode_attempts = 0  # Initialize passcode_attempts if it's None

        if current_user.passcode_attempts >= 10:
            flash('Too many failed attempts. Please contact support.', 'danger')
            return redirect(url_for('main.profile'))
        try:
            group = Group.query.filter_by(passcode=form.passcode.data).first()
            if not group:
                current_user.passcode_attempts += 1
                db.session.commit()
                flash('Invalid passcode. Please try again.', 'danger')
                return redirect(url_for('main.join_group'))
        
            current_user.group = group
            current_user.passcode_attempts = 0  # Reset attempts on successful joining
            db.session.commit()
            flash('You have successfully joined the group!', 'success')
            return redirect(url_for('main.profile'))
        except Exception as e:
            print("Failed to process request or insert to db")
    return render_template('join_group.html', title='Join Group', form=form)

@main.route('/friends', methods=['GET'])
@login_required
def friends():
    if not current_user.group_id:
        flash('You are not part of any group', 'warning')
        return redirect(url_for('main.index'))
    
    users = User.query.filter_by(group_id=current_user.group_id).all()
    return render_template('friends.html', users=users)