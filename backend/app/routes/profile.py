from flask import Blueprint, request, jsonify, url_for, current_app
from flask_login import login_required, current_user
from ..models import User
from ..forms import UpdateProfileForm
from ..extensions import db
import secrets, os
from PIL import Image
from .auth import token_required

profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/api/profile', methods=['GET', 'POST'])
@token_required
def profile(current_user):
    if request.method == 'POST':
        data = request.get_json()
        form = UpdateProfileForm(data=data, formdata=None)
        if form.validate():
            try:
                if 'profile_image' in data:
                    picture_file = save_picture(data['profile_image'], 'static/profile_pics')
                    current_user.profile_image = picture_file
                current_user.username = form.username.data
                current_user.email = form.email.data
                current_user.note = form.note.data
                db.session.commit()
                return jsonify({'message': 'Your account has been updated!', 'status': 'success'})
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': f'An error occurred: {str(e)}', 'status': 'danger'}), 500
        return jsonify({'error': 'Invalid form data'}), 400
    elif request.method == 'GET':
        profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image) if current_user.profile_image else None
        return jsonify({
            'username': current_user.username,
            'email': current_user.email,
            'note': current_user.note,
            'profile_image': profile_image
        })

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
