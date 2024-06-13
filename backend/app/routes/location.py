from flask import Blueprint, render_template, jsonify, request, url_for, current_app
from flask_login import login_required, current_user
from ..models import Location, MeetingPoint, StaticLocation, User, Group
from ..extensions import db
from datetime import datetime, timedelta
import pytz
import os
import secrets
from PIL import Image

location_bp = Blueprint('location_bp', __name__)

@location_bp.route('/test-location', methods=['GET'])
@login_required
def test_location():
    return render_template('test-location.html')


@location_bp.route('/update', methods=['POST'])
@login_required
def update_location():
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if latitude and longitude:
            location = Location.query.filter_by(user_id=current_user.id).order_by(Location.timestamp.desc()).first()
            if location:
                location.latitude = latitude
                location.longitude = longitude
                location.timestamp = datetime.now()  # Use UTC for consistency
            else:
                location = Location(
                    user_id=current_user.id,
                    latitude=latitude,
                    longitude=longitude,
                    timestamp=datetime.now()
                )
                db.session.add(location)
            db.session.commit()
            return jsonify({'message': 'Location updated successfully'}), 200

        return jsonify({'message': 'Invalid data'}), 400
    except Exception as e:
        print(f"Error with updating location - {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

@location_bp.route('/data', methods=['GET'])
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

@location_bp.route('/<int:user_id>', methods=['GET'])
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

@location_bp.route('/locations', methods=['GET'])
@login_required
def get_locations():
    if not current_user.group_id:
        return jsonify({'locations': []})

    def format_time(dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def calculate_remaining_time(created_at, duration):
        expires_at = created_at + timedelta(hours=duration)
        remaining = expires_at - datetime.now()
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
            'profile_image': url_for('static', filename='static/static_pics/' + (location.image if location.image else 'default_static.png')),
            'note': location.note,
            'isMeetingPoint': False,
            'created_at': None,
            'remaining_time': None
        })

    return jsonify({'locations': locations})

@location_bp.route('/create_location', methods=['POST'])
@login_required
def create_location():
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    username = request.form.get('username')
    note = request.form.get('note')
    loc_type = request.form.get('locType')
    image = request.files.get('image')
    duration = request.form.get('duration') if loc_type == 'meetingPoint' else None

    # Logging received form data
    print(f"Received data: latitude={latitude}, longitude={longitude}, username={username}, note={note}, loc_type={loc_type}, image={image}, duration={duration}")

    if not (latitude and longitude and username and loc_type):
        return jsonify({'message': 'Invalid data'}), 400

    image_filename = None
    if image:
        target_dir = 'static/meeting_pics' if loc_type == 'meetingPoint' else 'static/static_pics'
        try:
            image_filename = save_picture(image, target_dir)
        except ValueError as e:
            return jsonify({'message': str(e)}), 400

    try:
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
        print("Location created successfully")
        return jsonify({'message': 'Location created successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'message': 'Failed to create location', 'error': str(e)}), 500

@location_bp.route('/delete_meeting_point/<int:meeting_point_id>', methods=['POST'])
@login_required
def delete_meeting_point(meeting_point_id):
    if not current_user.is_superuser:
        return jsonify({'message': 'Permission denied'}), 403

    meeting_point = MeetingPoint.query.get_or_404(meeting_point_id)
    db.session.delete(meeting_point)
    db.session.commit()
    return jsonify({'message': 'Meeting point deleted successfully'}), 200

@location_bp.route('/delete_static_location/<int:location_id>', methods=['POST'])
@login_required
def delete_static_location(location_id):
    if not current_user.is_superuser:
        return jsonify({'message': 'Permission denied'}), 403

    static_location = StaticLocation.query.get_or_404(location_id)
    db.session.delete(static_location)
    db.session.commit()
    return jsonify({'message': 'Static location deleted successfully'}), 200

@location_bp.route('/static_locations', methods=['GET'])
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
            'image': url_for('static', filename='static/static_pics/' + (location.image if location.image else 'default_static.png'))
        })

    return jsonify({'locations': locations})

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
