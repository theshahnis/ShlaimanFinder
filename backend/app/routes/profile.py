from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from ..models import User
from ..forms import UpdateProfileForm
from ..extensions import db
from PIL import Image
import secrets
import os

profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        try:
            if 'profile_image' in request.files:
                picture_file = save_picture(request.files['profile_image'], 'static/profile_pics')
                current_user.profile_image = picture_file
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.note = form.note.data
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
    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image) if current_user.profile_image else None
    return render_template('profile.html', title='Profile', form=form, profile_image=profile_image)

def save_picture(form_picture, target_dir):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, target_dir, picture_fn)

    if not os.path.exists(os.path.join(current_app.root_path, target_dir)):
        os.makedirs(os.path.join(current_app.root_path, target_dir))

    print(f"Saving picture to: {picture_path}")  # Debug statement

    try:
        with Image.open(form_picture) as img:
            img.verify()
            form_picture.seek(0)

            # Resize and compress the image
            max_size_kb = 700
            target_width, target_height = 525, 700
            img = img.convert("RGB")  # Ensure image is in RGB mode
            img.thumbnail((target_width, target_height), Image.ANTIALIAS)

            # Save the image with reduced quality
            img.save(picture_path, optimize=True, quality=85)
            if os.path.getsize(picture_path) > max_size_kb * 1024:
                img.save(picture_path, optimize=True, quality=75)

            print("Image verified successfully")  # Debug statement
    except (IOError, SyntaxError) as e:
        print(f"Invalid image file: {e}")  # Debug statement
        raise ValueError("Invalid image file")

    form_picture.save(picture_path)
    print(f"Image saved to: {picture_path}")  # Debug statement
    return picture_fn
