from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import User, Group
from ..extensions import db
from werkzeug.security import generate_password_hash

superuser_bp = Blueprint('superuser_bp', __name__)

@superuser_bp.route('/', methods=['GET'])
@login_required
def superuser_view():
    if not current_user.superuser:
        flash('Access denied: Superuser only', 'error')
        return redirect(url_for('general_bp.index'))
    users = User.query.all()
    groups = Group.query.all()
    return render_template('superuser.html', users=users, groups=groups)

@superuser_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
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
