from flask import Blueprint, render_template, redirect, url_for, flash, request,current_app
from flask_login import login_required, current_user
from ..models import User
from ..forms import UpdateProfileForm
from ..extensions import db
import secrets,os
from PIL import Image

profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/', methods=['GET', 'POST'])
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
    f_ext = f_ext.lower()  # Ensure the extension is in lower case

    if f_ext in ['.jpeg', '.jpg']:
        picture_fn = f"{random_hex}.jpg"  # Convert JPEG to JPG
    else:
        picture_fn = f"{random_hex}{f_ext}"  # Keep original extension for other formats

    picture_path = os.path.join(current_app.root_path, target_dir, picture_fn)

    if not os.path.exists(os.path.join(current_app.root_path, target_dir)):
        os.makedirs(os.path.join(current_app.root_path, target_dir))

    try:
        with Image.open(form_picture) as img:
            img.verify()
            form_picture.seek(0)
            img = Image.open(form_picture)

            if f_ext in ['.jpeg', '.jpg']:
                img = img.convert('RGB')  # Ensure image is in RGB format
                img.save(picture_path, 'JPEG')  # Save as JPEG
            else:
                img.save(picture_path)  # Save in original format
    except (IOError, SyntaxError) as e:
        raise ValueError(f"Invalid image file: {e}")
    except PermissionError as e:
        raise ValueError(f"Permission denied: {e}")
    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {e}")

    return picture_fn
