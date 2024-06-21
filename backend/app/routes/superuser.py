from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..models import User, Group, StaticLocation, MeetingPoint
from ..extensions import db
from werkzeug.security import generate_password_hash
from .api import token_or_login_required
from flask_restx import Resource, Namespace, fields

superuser_bp = Blueprint('superuser_bp', __name__,url_prefix='/superuser')
superuser_ns = Namespace('superuser', description='Superuser operations')

user_model = superuser_ns.model('User', {
    'id': fields.Integer(required=True, description='User ID'),
    'email': fields.String(required=True, description='User email'),
    'username': fields.String(required=True, description='Username'),
    'group_id': fields.Integer(description='Group ID')
})

group_model = superuser_ns.model('Group', {
    'id': fields.Integer(required=True, description='Group ID'),
    'name': fields.String(required=True, description='Group name'),
    'passcode': fields.String(description='Group passcode')
})

static_location_model = superuser_ns.model('StaticLocation', {
    'id': fields.Integer(required=True, description='Static location ID'),
    'name': fields.String(required=True, description='Static location name'),
    'latitude': fields.Float(required=True, description='Latitude'),
    'longitude': fields.Float(required=True, description='Longitude'),
    'note': fields.String(description='Note about the location')
})

meeting_point_model = superuser_ns.model('MeetingPoint', {
    'id': fields.Integer(required=True, description='Meeting point ID'),
    'username': fields.String(required=True, description='Username who created the meeting point'),
    'note': fields.String(description='Note about the meeting point'),
    'created_at': fields.DateTime(description='Creation time of the meeting point'),
    'remaining_time': fields.Integer(description='Remaining time for the meeting point'),
    'isMeetingPoint': fields.Boolean(description='Is this a meeting point')
})

location_model = superuser_ns.model('Location', {
    'locations': fields.List(fields.Nested(static_location_model))
})

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

@superuser_bp.route('/delete_meeting_point', methods=['POST'])
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


@superuser_ns.route('/api')
class SuperuserAPIResource(Resource):
    @superuser_ns.doc('get_superuser_data')
    @superuser_ns.marshal_with(superuser_ns.model('SuperuserData', {
        'users': fields.List(fields.Nested(user_model)),
        'groups': fields.List(fields.Nested(group_model)),
        'static_locations': fields.List(fields.Nested(static_location_model)),
        'meeting_points': fields.List(fields.Nested(meeting_point_model))
    }))
    def get(self):
        return superuser_api()

@superuser_ns.route('/edit/<int:user_id>')
class EditUserResource(Resource):
    @superuser_ns.doc('edit_user')
    @superuser_ns.expect(superuser_ns.model('EditUserPayload', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(description='New password'),
        'group_id': fields.Integer(description='Group ID')
    }))
    def put(self, user_id):
        return edit_user(user_id)

@superuser_ns.route('/delete/<int:user_id>')
class DeleteUserResource(Resource):
    @superuser_ns.doc('delete_user')
    def delete(self, user_id):
        return delete_user(user_id)

@superuser_ns.route('/add_group')
class AddGroupResource(Resource):
    @superuser_ns.doc('add_group')
    @superuser_ns.expect(superuser_ns.model('AddGroupPayload', {
        'group_name': fields.String(required=True, description='Group name'),
        'passcode': fields.String(description='Group passcode')
    }))
    def post(self):
        return add_group()

@superuser_ns.route('/delete_static_location')
class DeleteStaticLocationResource(Resource):
    @superuser_ns.doc('delete_static_location')
    @superuser_ns.expect(superuser_ns.model('DeleteStaticLocationPayload', {
        'location_id': fields.Integer(required=True, description='Static location ID')
    }))
    def post(self):
        return delete_static_location()

@superuser_ns.route('/delete_meeting_point')
class DeleteMeetingPointResource(Resource):
    @superuser_ns.doc('delete_meeting_point')
    @superuser_ns.expect(superuser_ns.model('DeleteMeetingPointPayload', {
        'location_id': fields.Integer(required=True, description='Meeting point ID')
    }))
    def post(self):
        return delete_meeting_point()

@superuser_ns.route('/locations')
class GetLocationsResource(Resource):
    @superuser_ns.doc('get_locations')
    @superuser_ns.marshal_with(superuser_ns.model('LocationsData', {
        'locations': fields.List(fields.Nested(fields.Raw))
    }))
    def get(self):
        return get_locations()

@superuser_ns.route('/add_static_location')
class AddStaticLocationResource(Resource):
    @superuser_ns.doc('add_static_location')
    @superuser_ns.expect(superuser_ns.model('AddStaticLocationPayload', {
        'name': fields.String(required=True, description='Static location name'),
        'latitude': fields.Float(required=True, description='Latitude'),
        'longitude': fields.Float(required=True, description='Longitude'),
        'note': fields.String(description='Note about the location'),
        'image': fields.String(description='Image of the location')
    }))
    def post(self):
        return add_static_location()