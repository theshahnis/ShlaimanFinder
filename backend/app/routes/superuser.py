from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..models import User, Group, StaticLocation, MeetingPoint
from ..extensions import db
from werkzeug.security import generate_password_hash

superuser_bp = Blueprint('superuser_bp', __name__)

@superuser_bp.route('/', methods=['GET'])
@token_required
def superuser_view():
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('general_bp.index'))
    users = User.query.all()
    groups = Group.query.all()
    static_locations = StaticLocation.query.all()
    meeting_points = MeetingPoint.query.all()
    return render_template('superuser.html', users=users, groups=groups, static_locations=static_locations, meeting_points=meeting_points)

@superuser_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@token_required
def edit_user(user_id):
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('general_bp.index'))

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
        return redirect(url_for('superuser_bp.superuser_view'))

    return render_template('edit_user.html', user=user, groups=groups)

@superuser_bp.route('/delete/<int:user_id>', methods=['POST'])
@token_required
def delete_user(user_id):
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('general_bp.index'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('superuser_bp.superuser_view'))

@superuser_bp.route('/add_group', methods=['POST'])
@token_required
def add_group():
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('general_bp.index'))
    group_name = request.form['group_name']
    passcode = request.form['passcode']
    new_group = Group(name=group_name, passcode=passcode)
    db.session.add(new_group)
    db.session.commit()
    flash('Group added successfully', 'success')
    return redirect(url_for('superuser_bp.superuser_view'))

@superuser_bp.route('/delete_static_location/<int:location_id>', methods=['POST'])
@token_required
def delete_static_location(location_id):
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('general_bp.index'))
    location = StaticLocation.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    flash('Static location deleted successfully', 'success')
    return redirect(url_for('superuser_bp.superuser_view'))

@superuser_bp.route('/delete_meeting_point/<int:point_id>', methods=['POST'])
@token_required
def delete_meeting_point(point_id):
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('general_bp.index'))
    point = MeetingPoint.query.get_or_404(point_id)
    db.session.delete(point)
    db.session.commit()
    flash('Meeting point deleted successfully', 'success')
    return redirect(url_for('superuser_bp.superuser_view'))

@superuser_bp.route('/locations', methods=['GET'])
@token_required
def get_locations():
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('general_bp.index'))
    meeting_points = MeetingPoint.query.all()
    static_locations = StaticLocation.query.all()
    locations = []
    for mp in meeting_points:
        locations.append({
            'id': mp.id,
            'username': mp.username,
            'note': mp.note,
            'created_at': mp.created_at,
            'remaining_time': mp.duration,  # Assuming you have a way to calculate remaining time
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
@token_required
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
