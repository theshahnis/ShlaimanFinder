import os
import secrets
from flask import current_app, Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from .models import User
from .extensions import mongo
from .forms import UpdateProfileForm

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('index.html', name=current_user['username'])

@main.before_request
def before_request():
    if not current_user.is_authenticated and request.endpoint != 'auth.auth_page':
        return redirect(url_for('auth.auth_page'))


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        update_data = {
            "username": form.username.data,
            "email": form.email.data
        }
        if form.profile_image.data:
            picture_file = save_picture(form.profile_image.data)
            update_data["profile_image"] = picture_file
        mongo.db.users.update_one({"_id": current_user['_id']}, {"$set": update_data})
        flash('Your account has been updated!', 'success')
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.username.data = current_user['username']
        form.email.data = current_user['email']
    profile_image = url_for('static', filename='profile_pics/' + current_user.get('profile_image', '')) if current_user.get('profile_image') else None
    return render_template('profile.html', title='Profile', form=form, profile_image=profile_image)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@main.route('/superuser')
@login_required
def superuser():
    if not current_user['superuser']:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('main.profile'))
    users = mongo.db.users.find()
    groups = mongo.db.groups.find()
    return render_template('superuser.html', users=users, groups=groups)

@main.route('/superuser/edit/<string:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user['superuser']:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('main.profile'))
    user = mongo.db.users.find_one({"_id": user_id})
    if request.method == 'POST':
        update_data = {
            "email": request.form['email']
        }
        if request.form['password']:
            update_data["password"] = generate_password_hash(request.form['password'])
        mongo.db.users.update_one({"_id": user_id}, {"$set": update_data})
        flash('User updated successfully', 'success')
        return redirect(url_for('main.superuser'))
    return render_template('edit_user.html', user=user, groups=mongo.db.groups.find())

@main.route('/superuser/delete/<string:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user['superuser']:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('main.profile'))
    mongo.db.users.delete_one({"_id": user_id})
    flash('User deleted successfully', 'success')
    return redirect(url_for('main.superuser'))

@main.route('/superuser/add_group', methods=['POST'])
@login_required
def add_group():
    if not current_user['superuser']:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('main.profile'))
    group_name = request.form['group_name']
    new_group = {"name": group_name}
    mongo.db.groups.insert_one(new_group)
    flash('Group added successfully', 'success')
    return redirect(url_for('main.superuser'))

@main.route('/location', methods=['GET'])
@login_required
def location():
    return render_template('location.html')

@main.route('/location', methods=['POST'])
@login_required
def update_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    # Here, you can handle the received location data as needed
    return jsonify({'message': 'Location updated successfully'}), 200
