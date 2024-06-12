from flask import Blueprint, render_template, redirect, url_for, flash, request,current_app
from flask_login import login_required, current_user
from ..models import User
from ..forms import UpdateProfileForm
from ..extensions import db
import secrets,os,logging
from PIL import Image

logging.basicConfig(level=logging.INFO)

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
    f_ext = f_ext.lower()

    try:
        if f_ext in ['.jpeg', '.jpg']:
            picture_fn = f"{random_hex}.jpg"  # Convert JPEG to JPG
        else:
            picture_fn = f"{random_hex}{f_ext}"  # Keep original extension for other formats
    except Exception as e:
        logging.error(f"Failed processing image extension: {f_ext} - {e}")
        raise ValueError(f"Failed processing image extension: {f_ext} - {e}")

    picture_path = os.path.join(current_app.root_path, target_dir, picture_fn)

    if not os.path.exists(os.path.join(current_app.root_path, target_dir)):
        os.makedirs(os.path.join(current_app.root_path, target_dir))
        logging.info(f"Created directory: {os.path.join(current_app.root_path, target_dir)}")

    try:
        # Save the uploaded file first
        form_picture.save(picture_path)
        logging.info(f"Saved file to {picture_path}")
    except Exception as e:
        logging.error(f"Failed to save file: {e}")
        raise ValueError(f"Failed to save file: {e}")

    try:
        # Open and verify the image after saving
        with Image.open(picture_path) as img:
            img.verify()
            logging.info(f"Verified image file at {picture_path}")

        # Re-open image for processing
        with Image.open(picture_path) as img:
            if f_ext in ['.jpeg', '.jpg']:
                img = img.convert('RGB')  # Ensure image is in RGB format
                img.save(picture_path, 'JPEG')  # Save as JPEG
                logging.info(f"Converted and saved image as JPEG at {picture_path}")
            else:
                img.save(picture_path)  # Save in original format
                logging.info(f"Saved image in original format at {picture_path}")
    except (IOError, SyntaxError) as e:
        logging.error(f"Invalid image file: {e}")
        raise ValueError(f"Invalid image file: {e}")
    except PermissionError as e:
        logging.error(f"Permission denied: {e}")
        raise ValueError(f"Permission denied: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise ValueError(f"An unexpected error occurred: {e}")

    return picture_fn