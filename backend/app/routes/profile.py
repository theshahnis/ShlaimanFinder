from flask import Blueprint, request, jsonify, url_for, current_app
from flask_login import login_required, current_user
from ..models import User
from ..forms import UpdateProfileForm
from ..extensions import db
import secrets, os
from PIL import Image

profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    user = {
        'username': current_user.username,
        'email': current_user.email,
        'note': current_user.note,
        'profile_image': url_for('static', filename='profile_pics/' + current_user.profile_image) if current_user.profile_image else None
    }
    return jsonify(user)

@profile_bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json()
    try:
        if 'profile_image' in data:
            picture_file = save_picture(data['profile_image'], 'static/profile_pics')
            current_user.profile_image = picture_file
        current_user.username = data['username']
        current_user.email = data['email']
        current_user.note = data['note']
        db.session.commit()
        return jsonify({'message': 'Your account has been updated!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

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
