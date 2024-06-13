from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ..models import User, Show, UserShow
from ..extensions import db
from datetime import datetime, timedelta
import pytz

show_bp = Blueprint('show_bp', __name__)

@show_bp.route('/', methods=['GET'])
@login_required
def shows():
    return render_template('shows.html')

@show_bp.route('/api/shows', methods=['GET'])
@login_required
def get_shows():
    date_str = request.args.get('date')
    show_id = request.args.get('id')

    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Amsterdam'))
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

        next_day = date + timedelta(days=1)
        shows = Show.query.filter(
            Show.start_time >= date,
            Show.start_time < next_day + timedelta(hours=6)  # Include shows that end up to 6 AM the next day
        ).all()
    elif show_id:
        show = Show.query.get(show_id)
        if not show:
            return jsonify({'error': 'Show not found'}), 404
        shows = [show]
    else:
        return jsonify({'error': 'Date or Show ID parameter is required'}), 400

    shows_data = []
    shows_attendees = {}

    for show in shows:
        show_dict = show.to_dict()
        shows_data.append(show_dict)

        # Fetch attendees for the show
        attendees = User.query.join(UserShow).filter(UserShow.show_id == show.id).all()
        shows_attendees[show.id] = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees]

    return jsonify({'shows': shows_data, 'shows_attendees': shows_attendees})

@show_bp.route('/api/show', methods=['GET'])
@login_required
def get_show():
    show_id = request.args.get('id')
    if not show_id:
        return jsonify({'error': 'Show ID is required'}), 400
    
    show = Show.query.get(show_id)
    if not show:
        return jsonify({'error': 'Show not found'}), 404
    
    show_dict = show.to_dict()
    
    attendees = User.query.join(UserShow).filter(UserShow.show_id == show.id).all()
    attendees_data = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees]

    return jsonify({'show': show_dict, 'attendees': attendees_data})

@show_bp.route('/user-shows', methods=['GET'])
@login_required
def user_shows():
    user_id = current_user.id
    user_shows = UserShow.query.filter_by(user_id=user_id).all()
    show_ids = [user_show.show_id for user_show in user_shows]
    shows_attendees = {}
    for show_id in show_ids:
        attendees = User.query.join(UserShow).filter(UserShow.show_id == show_id).all()
        shows_attendees[show_id] = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees]
    return jsonify({'show_ids': show_ids, 'shows_attendees': shows_attendees})

@show_bp.route('/select-show', methods=['POST'])
@login_required
def select_show():
    data = request.json
    show_id = data.get('showId')
    action = data.get('action')
    user_id = current_user.id

    user_show = UserShow.query.filter_by(user_id=user_id, show_id=show_id).first()

    if action == 'attend' and not user_show:
        user_show = UserShow(user_id=user_id, show_id=show_id)
        db.session.add(user_show)
    elif action == 'leave' and user_show:
        db.session.delete(user_show)
    
    db.session.commit()

    attendees = User.query.join(UserShow).filter(UserShow.show_id == show_id).all()
    attendees_data = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees]
    
    return jsonify({'attendees': attendees_data})

@show_bp.route('/my-shows', methods=['GET'])
@login_required
def my_shows():
    return render_template('my_shows.html')

@show_bp.route('/api/my-shows', methods=['GET'])
@login_required
def get_my_shows():
    user_id = current_user.id
    now = datetime.now(pytz.timezone('Europe/Amsterdam'))
    user_shows = UserShow.query.join(Show).filter(
        UserShow.user_id == user_id,
        Show.start_time >= now
    ).order_by(Show.start_time).all()

    shows_data = []
    for user_show in user_shows:
        show = user_show.show
        shows_data.append(show.to_dict())

    return jsonify({'shows': shows_data})
