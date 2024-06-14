import os
import secrets
from flask import current_app, Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from .models import User, Group, Location, MeetingPoint, StaticLocation, Show, UserShow
from .extensions import db
from .forms import UpdateProfileForm, JoinGroupForm
from datetime import datetime, timedelta
from pytz import timezone
from PIL import Image
import pytz
main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('index.html', name=current_user.username)

@main.before_request
def before_request():
    if not current_user.is_authenticated and request.endpoint != 'auth_bp.auth_page':
        return redirect(url_for('auth_bp.auth_page'))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        try:
            if form.profile_image.data:
                picture_file = save_picture(form.profile_image.data, 'static/profile_pics')
                current_user.profile_image = picture_file
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.note = form.note.data
            db.session.commit()
            flash('Your account has been updated!', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            db.session.rollback()
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.note.data = current_user.note
    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image) if current_user.profile_image else None
    return render_template('profile.html', title='Profile', form=form, profile_image=profile_image)

def save_picture(form_picture, target_dir):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, target_dir, picture_fn)

    if not os.path.exists(os.path.join(current_app.root_path, target_dir)):
        os.makedirs(os.path.join(current_app.root_path, target_dir))

    try:
        with Image.open(form_picture) as img:
            img.verify()
            form_picture.seek(0)
    except (IOError, SyntaxError) as e:
        raise ValueError("Invalid image file")

    form_picture.save(picture_path)
    return picture_fn

@main.route('/superuser', methods=['GET'])
@login_required
def superuser():
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('main.index'))
    users = User.query.all()
    groups = Group.query.all()
    return render_template('superuser.html', users=users, groups=groups)

@main.route('/superuser/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_superuser:
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
    if not current_user.is_superuser:
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
    if not current_user.is_superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('main.profile'))
    group_name = request.form['group_name']
    passcode = request.form['passcode']
    new_group = Group(name=group_name, passcode=passcode)
    db.session.add(new_group)
    db.session.commit()
    flash('Group added successfully', 'success')
    return redirect(url_for('main.superuser'))

@main.route('/test-location', methods=['GET'])
@login_required
def location():
    return render_template('test-location.html')

@main.route('/location', methods=['POST'])
@login_required
def update_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if latitude and longitude:
        location = Location.query.filter_by(user_id=current_user.id).order_by(Location.timestamp.desc()).first()
        if location:
            location.latitude = latitude
            location.longitude = longitude
            location.timestamp = datetime.utcnow()  # Use UTC for consistency
        else:
            location = Location(
                user_id=current_user.id,
                latitude=latitude,
                longitude=longitude,
                timestamp=datetime.utcnow()
            )
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

@main.route('/locations', methods=['GET'])
@login_required
def get_locations():
    if not current_user.group_id:
        return jsonify({'locations': []})

    def format_time(dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def calculate_remaining_time(created_at, duration):
        expires_at = created_at + timedelta(hours=duration)
        remaining = expires_at - datetime.utcnow()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)

    users = User.query.filter_by(group_id=current_user.group_id).all()
    locations = []
    for user in users:
        location = Location.query.filter_by(user_id=user.id).order_by(Location.timestamp.desc()).first()
        if location:
            locations.append({
                'username': user.username,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'profile_image': url_for('static', filename='profile_pics/' + (user.profile_image if user.profile_image else 'default.png')),
                'note': user.note,
                'isMeetingPoint': False,
                'created_at': format_time(location.timestamp),
                'remaining_time': None
            })

    meeting_points = MeetingPoint.query.filter_by(group_id=current_user.group_id).all()
    for point in meeting_points:
        remaining_time = calculate_remaining_time(point.created_at, point.duration)
        if remaining_time.total_seconds() > 0:
            locations.append({
                'username': point.username,
                'latitude': point.latitude,
                'longitude': point.longitude,
                'profile_image': url_for('static', filename='meeting_pics/' + (point.image if point.image else 'default_meeting_point.png')),
                'note': point.note,
                'isMeetingPoint': True,
                'created_at': format_time(point.created_at),
                'remaining_time': str(remaining_time)
            })

    static_locations = StaticLocation.query.all()
    for location in static_locations:
        locations.append({
            'username': location.name,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'profile_image': url_for('static', filename='static_pics/' + (location.image if location.image else 'static_location.jpg')),
            'note': location.note,
            'isMeetingPoint': False,
            'created_at': None,
            'remaining_time': None
        })

    return jsonify({'locations': locations})



@main.route('/create_location', methods=['POST'])
@login_required
def create_location():
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    username = request.form.get('username')
    note = request.form.get('note')
    loc_type = request.form.get('locType')
    image = request.files.get('image')
    duration = request.form.get('duration') if loc_type == 'meetingPoint' else None

    if not (latitude and longitude and username and loc_type):
        return jsonify({'message': 'Invalid data'}), 400

    image_filename = None
    if image:
        target_dir = 'static/meeting_pics' if loc_type == 'meetingPoint' else 'static/static_pics'
        try:
            image_filename = save_picture(image, target_dir)
        except ValueError as e:
            return jsonify({'message': str(e)}), 400

    if loc_type == 'meetingPoint':
        meeting_point = MeetingPoint(
            latitude=latitude,
            longitude=longitude,
            username=username,
            note=note,
            image=image_filename,
            group_id=current_user.group_id,
            duration=int(duration)
        )
        db.session.add(meeting_point)
    else:
        static_location = StaticLocation(
            latitude=latitude,
            longitude=longitude,
            name=username,
            note=note,
            image=image_filename
        )
        db.session.add(static_location)

    db.session.commit()

    return jsonify({'message': 'Location created successfully'}), 200

@main.route('/delete_meeting_point/<int:meeting_point_id>', methods=['POST'])
@login_required
def delete_meeting_point(meeting_point_id):
    if not current_user.is_superuser:
        return jsonify({'message': 'Permission denied'}), 403

    meeting_point = MeetingPoint.query.get_or_404(meeting_point_id)
    db.session.delete(meeting_point)
    db.session.commit()
    return jsonify({'message': 'Meeting point deleted successfully'}), 200

@main.route('/delete_static_location/<int:location_id>', methods=['POST'])
@login_required
def delete_static_location(location_id):
    if not current_user.is_superuser:
        return jsonify({'message': 'Permission denied'}), 403

    static_location = StaticLocation.query.get_or_404(location_id)
    db.session.delete(static_location)
    db.session.commit()
    return jsonify({'message': 'Static location deleted successfully'}), 200

@main.route('/static_locations', methods=['GET'])
@login_required
def get_static_locations():
    static_locations = StaticLocation.query.all()
    locations = []
    for location in static_locations:
        locations.append({
            'id': location.id,
            'name': location.name,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'note': location.note,
            'image': url_for('static', filename='static/static_pics/' + (location.image if location.image else 'static_location.jpg'))
        })

    return jsonify({'locations': locations})

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

@main.route('/map', methods=['GET'])
@login_required
def map_view():
    return render_template('map.html')

@main.route('/shows', methods=['GET'])
@login_required
def shows():
    return render_template('shows.html')

@main.route('/api/shows', methods=['GET'])
@login_required
def get_shows():
    date_str = request.args.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Amsterdam'))
    next_day = date + timedelta(days=1)
    shows = Show.query.filter(
        Show.start_time >= date,
        Show.start_time < next_day + timedelta(hours=6)  # Include shows that end up to 6 AM the next day
    ).all()
    shows_data = [show.to_dict() for show in shows]
    return jsonify({'shows': shows_data})

@main.route('/user-shows', methods=['GET'])
@login_required
def user_shows():
    user_id = current_user.id
    user_shows = UserShow.query.filter_by(user_id=user_id).all()
    show_ids = [user_show.show_id for user_show in user_shows]
    shows_attendees = {}
    for show_id in show_ids:
        attendees = User.query.join(UserShow).filter(UserShow.show_id == show_id).all()
        shows_attendees[show_id] = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees]
    return jsonify({'show_ids': show_ids, 'shows_attendees': shows_attendees})

@main.route('/select-show', methods=['POST'])
@login_required
def select_show():
    data = request.json
    show_id = data.get('showId')
    action = data.get('action')
    user_id = current_user.id

    user_show = UserShow.query.filter_by(user_id=user_id, show_id=show_id).first()

    if action == 'attend' and not user_show:
        user_show = UserShow(user_id=user_id, show_id=show_id)
        db.session.add(user_show)
    elif action == 'leave' and user_show:
        db.session.delete(user_show)
    
    db.session.commit()

    attendees = User.query.join(UserShow).filter(UserShow.show_id == show_id).all()
    attendees_data = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees]
    
    return jsonify({'attendees': attendees_data})