from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_restx import Resource, Namespace, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import login_required, current_user
from ..models import User
from ..forms import UpdateProfileForm
from ..extensions import db
import secrets, os
from PIL import Image
from .api import token_or_login_required

profile_bp = Blueprint('profile_bp', __name__)
profile_ns = Namespace('profile', description='Profile related operations')

profile_model = profile_ns.model('Profile', {
    'username': fields.String(required=True, description='The username'),
    'email': fields.String(required=True, description='The email address'),
    'note': fields.String(description='A note about the user'),
    'profile_image': fields.String(description='URL to the profile image'),
    'phone_number': fields.String(description='The phone number')
})

# HTML Profile Route
@profile_bp.route('/', methods=['GET', 'POST'])
@token_or_login_required
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
            phone_number = form.phone_number.data
            if phone_number.startswith('0'):
                phone_number = phone_number[1:]
            current_user.phone_number = '+972' + phone_number
            db.session.commit()
            flash('Your account has been updated!', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            db.session.rollback()
        return redirect(url_for('profile_bp.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.note.data = current_user.note
        form.phone_number.data = current_user.phone_number
    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image) if current_user.profile_image else None
    return render_template('profile.html', title='Profile', form=form, profile_image=profile_image)

# API Profile Routes
@profile_bp.route('/api', methods=['GET'])
@token_or_login_required
def get_profile_api():
    """Get the current user's profile (API)"""
    user = current_user
    profile_image = url_for('static', filename='profile_pics/' + user.profile_image) if user.profile_image else None
    return jsonify({
        'username': user.username,
        'email': user.email,
        'note': user.note,
        'phone_number': user.phone_number,
        'profile_image': profile_image
    }), 200

@profile_bp.route('/api', methods=['PUT'])
@token_or_login_required
def update_profile_api():
    """Update the current user's profile (API)"""
    data = request.form
    user = current_user
    user.username = data.get('username', user.username)
    phone_number = data.get('phone_number')
    if phone_number and phone_number.startswith('0'):
        phone_number = phone_number[1:]
    user.phone_number = '+972' + phone_number if phone_number else user.phone_number
    user.email = data.get('email', user.email)
    user.note = data.get('note', user.note)

    picture_file = None
    if 'profile_image' in request.files and request.files['profile_image'].filename != '':
        try:
            picture_file = save_picture(request.files['profile_image'], 'static/profile_pics')
        except ValueError as e:
            return jsonify({'message': str(e)}), 400

    if picture_file:
        user.profile_image = picture_file

    try:
        db.session.commit()
        response = {
            'message': 'Your account has been updated!',
            'profile': {
                'username': user.username,
                'email': user.email,
                'note': user.note,
                'phone_number': user.phone_number,
                'profile_image': url_for('static', filename='profile_pics/' + user.profile_image) if user.profile_image else None
            }
        }
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 400


def save_picture(form_picture, target_dir):
    if form_picture is None:
        return None

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

# API Namespace for documentation purposes only
@profile_ns.route('/api')
class UserProfileAPI(Resource):
    @profile_ns.doc('get_profile')
    @profile_ns.marshal_with(profile_model)
    @token_or_login_required
    def get(self):
        """Get the current user's profile"""
        user = current_user
        profile_image = url_for('static', filename='profile_pics/' + user.profile_image) if user.profile_image else None
        return {
            'username': user.username,
            'email': user.email,
            'note': user.note,
            'phone_number': user.phone_number,
            'profile_image': profile_image
        }

    @profile_ns.doc('update_profile')
    @profile_ns.expect(profile_model)
    @token_or_login_required
    def put(self):
        """Update the current user's profile"""
        data = request.get_json()
        user = current_user
        user.username = data.get('username', user.username)
        phone_number = data.get('phone_number')
        if phone_number and phone_number.startswith('0'):
            phone_number = phone_number[1:]
        user.phone_number = '+972' + phone_number if phone_number else user.phone_number
        user.email = data.get('email', user.email)
        user.note = data.get('note', user.note)

        if 'profile_image' in request.files:
            picture_file = save_picture(request.files['profile_image'], 'static/profile_pics')
            user.profile_image = picture_file

        try:
            db.session.commit()
            return {
                'username': user.username,
                'email': user.email,
                'note': user.note,
                'phone_number': user.phone_number,
                'profile_image': url_for('static', filename='profile_pics/' + user.profile_image) if user.profile_image else None
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'An error occurred: {str(e)}'}, 400