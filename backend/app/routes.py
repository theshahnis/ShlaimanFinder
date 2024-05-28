from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import User
from .extensions import db

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)


@main.before_request
def before_request():
    if not current_user.is_authenticated and request.endpoint != 'auth.auth_page':
        return redirect(url_for('auth.auth_page'))


@main.route('/superuser')
@login_required
def superuser():
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('main.profile'))
    users = User.query.all()
    return render_template('superuser.html', users=users)

@main.route('/superuser/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('main.profile'))
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.email = request.form['email']
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('main.superuser'))
    return render_template('edit_user.html', user=user)

@main.route('/superuser/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('main.profile'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('main.superuser'))
