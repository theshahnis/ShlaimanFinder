from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..models import User, Group, StaticLocation, MeetingPoint
from ..extensions import db
from werkzeug.security import generate_password_hash
from .api import token_or_login_required

superuser_bp = Blueprint('superuser_bp', __name__,url_prefix='/superuser')

@superuser_bp.route('/', methods=['GET'])
@token_or_login_required
def superuser_view():
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('general_bp.index'))
    users = User.query.all()
    groups = Group.query.all()
    static_locations = StaticLocation.query.all()
    meeting_points = MeetingPoint.query.all()
    return render_template('superuser.html', users=users, groups=groups, static_locations=static_locations, meeting_points=meeting_points)

# API route for superuser view
@superuser_bp.route('/api', methods=['GET'])
@token_or_login_required
def superuser_api():
    if not current_user.superuser:
        return jsonify({'error': 'Access denied: Superuser only'}), 403
    users = User.query.all()
    groups = Group.query.all()
    static_locations = StaticLocation.query.all()
    meeting_points = MeetingPoint.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users],
        'groups': [group.to_dict() for group in groups],
        'static_locations': [location.to_dict() for location in static_locations],
        'meeting_points': [point.to_dict() for point in meeting_points]
    })

@superuser_bp.route('/edit/<int:user_id>', methods=['GET', 'PUT'])
@token_or_login_required
def edit_user(user_id):
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('general_bp.index'))

    user = User.query.get_or_404(user_id)
    groups = Group.query.all()

    if request.method == 'PUT':
        data = request.get_json()
        user.email = data.get('email', user.email)
        if 'password' in data and data['password']:
            user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')
        user.group_id = data.get('group_id', user.group_id)
        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200

    return render_template('edit_user.html', user=user, groups=groups)


@superuser_bp.route('/delete/<int:user_id>', methods=['POST'])
@token_or_login_required
def delete_user(user_id):
    if not current_user.superuser:
        return jsonify({'error': 'Access denied: Superuser only'}), 403
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

@superuser_bp.route('/add_group', methods=['POST'])
@token_or_login_required
def add_group():
    if not current_user.superuser:
        return jsonify({'error': 'Access denied: Superuser only'}), 403
    
    data = request.get_json()
    group_name = data.get('group_name')
    passcode = data.get('passcode')

    existing_group = Group.query.filter_by(name=group_name).first()
    if existing_group:
        return jsonify({'error': 'Group name already exists. Please choose a different name.'}), 400

    new_group = Group(name=group_name, passcode=passcode)
    db.session.add(new_group)
    db.session.commit()
    return jsonify({'message': 'Group added successfully'}), 201

@superuser_bp.route('/delete_static_location', methods=['POST'])
@token_or_login_required
def delete_static_location():
    if not current_user.superuser:
        return jsonify({'error': 'Access denied: Superuser only'}), 403

    data = request.get_json()
    location_id = data.get('location_id')

    if not location_id:
        return jsonify({'error': 'Missing location_id'}), 400

    location = StaticLocation.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    return jsonify({'message': 'Static location deleted successfully'}), 200

@superuser_bp.route('/delete_meeting_point', methods=['DELETE'])
@token_or_login_required
def delete_meeting_point():
    if not current_user.superuser:
        return jsonify({'error': 'Access denied: Superuser only'}), 403

    data = request.get_json()
    point_id = data.get('location_id')

    if not point_id:
        return jsonify({'error': 'Missing location_id'}), 400

    point = MeetingPoint.query.get_or_404(point_id)
    db.session.delete(point)
    db.session.commit()
    return jsonify({'message': 'Meeting point deleted successfully'}), 200

@superuser_bp.route('/locations', methods=['GET'])
@token_or_login_required
def get_locations():
    if not current_user.superuser:
        return jsonify({'error': 'Access denied: Superuser only'}), 403

    meeting_points = MeetingPoint.query.all()
    static_locations = StaticLocation.query.all()
    locations = []
    for mp in meeting_points:
        locations.append({
            'id': mp.id,
            'username': mp.username,
            'note': mp.note,
            'created_at': mp.created_at,
            'remaining_time': mp.duration,
            'isMeetingPoint': True
        })
    for sl in static_locations:
        locations.append({
            'id': sl.id,
            'name': sl.name,
            'note': sl.note,
            'isMeetingPoint': False
        })
    return jsonify({'locations': locations})

@superuser_bp.route('/add_static_location', methods=['POST'])
@token_or_login_required
def add_static_location():
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('general_bp.index'))
    name = request.form.get('name')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    note = request.form.get('note')
    image = request.files.get('image')
    image_filename = None
    if image:
        target_dir = 'static/static_pics'
        try:
            image_filename = save_picture(image, target_dir)
        except ValueError as e:
            return jsonify({'message': str(e)}), 400
    static_location = StaticLocation(
        name=name,
        latitude=latitude,
        longitude=longitude,
        note=note,
        image=image_filename
    )
    db.session.add(static_location)
    db.session.commit()
    return jsonify({'message': 'Static location added successfully'})


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