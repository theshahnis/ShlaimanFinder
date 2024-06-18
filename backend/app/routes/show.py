from flask import Blueprint, render_template, redirect, url_for, flash, request,jsonify
from flask_login import login_required, current_user
from ..models import User,Location, MeetingPoint, StaticLocation, Show, UserShow
from ..forms import UpdateProfileForm
from ..extensions import db
from datetime import datetime, timedelta
import pytz
from .api import token_or_login_required
from flask_restx import Namespace, Resource, fields, Api


show_bp = Blueprint('show_bp', __name__, url_prefix='/show')
show_ns = Namespace('show', description='Show related operations')

show_model = show_ns.model('Show', {
    'id': fields.Integer,
    'name': fields.String,
    'start_time': fields.String,  
    'end_time': fields.String,    
    'stage': fields.String
})

attendee_model = show_ns.model('Attendee', {
    'id': fields.Integer,
    'avatarUrl': fields.String,
    'username': fields.String
})

shows_attendees_model = show_ns.model('ShowsAttendees', {
    'shows': fields.List(fields.Nested(show_model)),
    'shows_attendees': fields.Raw  
})

show_attendees_model = show_ns.model('ShowAttendees', {
    'show': fields.Nested(show_model),
    'attendees': fields.List(fields.Nested(attendee_model))
})

user_shows_model = show_ns.model('UserShows', {
    'show_ids': fields.List(fields.Integer, description='List of show IDs the user is attending'),
    'shows_attendees': fields.Nested(attendee_model, description='List of attendees for each show')
})

my_shows_model = show_ns.model('MyShows', {
    'shows': fields.List(fields.Nested(show_model)),
    'shows_attendees': fields.Raw  
})


@show_bp.route('/', methods=['GET'])
@token_or_login_required
def shows():
    return render_template('shows.html')


@show_bp.route('/my-shows', methods=['GET'])
@token_or_login_required
def my_shows():
    return render_template('my_shows.html')

@show_bp.route('/api/shows', methods=['GET'])
@token_or_login_required
def get_shows():
    # Define the date range for the shows
    start_date = datetime.strptime('2024-06-27', '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Amsterdam'))
    end_date = datetime.strptime('2024-06-30', '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Amsterdam')) + timedelta(days=1)

    # Initialize an empty dictionary to store shows grouped by stage and date
    shows_data = {}
    shows_attendees = {}

    # Loop through each day in the range and gather shows
    current_date = start_date
    while current_date < end_date:
        day_start = current_date.replace(hour=10, minute=0, second=0, microsecond=0)
        day_end = (current_date + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)

        shows = Show.query.filter(
            Show.start_time >= day_start,
            Show.start_time < day_end
        ).all()

        for show in shows:
            show_dict = show.to_dict()
            stage = show_dict['stage']

            # Determine the correct day bucket
            show_start = datetime.strptime(show_dict['start_time'], '%Y-%m-%d %H:%M')
            show_end = datetime.strptime(show_dict['end_time'], '%Y-%m-%d %H:%M')

            if show_start.hour < 6:
                show_start -= timedelta(days=1)
            
            show_date = show_start.strftime('%Y-%m-%d')  # Extract the date in YYYY-MM-DD format

            if stage not in shows_data:
                shows_data[stage] = {}
            if show_date not in shows_data[stage]:
                shows_data[stage][show_date] = []
            shows_data[stage][show_date].append({
                'id': show_dict['id'],
                'name': show_dict['name'],
                'start_time': show_dict['start_time'],
                'end_time': show_dict['end_time'],
                'stage': show_dict['stage']
            })

        # Fetch attendees for the show
        attendees = User.query.join(UserShow).filter(UserShow.show_id == show.id).all()
        #adding check for attendees in group
        attendees_in_group = [user for user in attendees if user.group_id == current_user.group_id]
        #shows_attendees[show.id] = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees]
        shows_attendees[show.id] = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees_in_group]

    return jsonify({'shows': shows_data, 'shows_attendees': shows_attendees})





@show_bp.route('/api/show', methods=['GET'])
@token_or_login_required
def get_show():
    show_id = request.args.get('id')
    if not show_id:
        return jsonify({'error': 'Show ID is required'}), 400
    
    show = Show.query.get(show_id)
    if not show:
        return jsonify({'error': 'Show not found'}), 404
    
    show_dict = show.to_dict()
    
    attendees = User.query.join(UserShow).filter(UserShow.show_id == show.id).all()
    attendees_in_group = [user for user in attendees if user.group_id == current_user.group_id]
    #attendees_data = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees]
    attendees_data = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees_in_group]

    return jsonify({'show': show_dict, 'attendees': attendees_data})





@show_bp.route('/user-shows', methods=['GET'])
@token_or_login_required
def user_shows():
    user_id = current_user.id
    user_shows = UserShow.query.filter_by(user_id=user_id).all()
    show_ids = [user_show.show_id for user_show in user_shows]
    shows_attendees = {}
    for show_id in show_ids:
        attendees = User.query.join(UserShow).filter(UserShow.show_id == show_id).all()
        #shows_attendees[show_id] = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees]
        attendees_in_group = [user for user in attendees if user.group_id == current_user.group_id]
        shows_attendees[show_id] = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees_in_group]
    return jsonify({'show_ids': show_ids, 'shows_attendees': shows_attendees})




@show_bp.route('/select-show', methods=['POST'])
@token_or_login_required
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
    #attendees_data = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees]
    attendees_in_group = [user for user in attendees if user.group_id == current_user.group_id]
    attendees_data = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees_in_group]
    return jsonify({'attendees': attendees_data})




@show_bp.route('api/my-shows', methods=['GET'])
@token_or_login_required
def get_my_shows():
    user_id = current_user.id
    now = datetime.now(pytz.timezone('Europe/Amsterdam'))
    user_shows = UserShow.query.join(Show).filter(
        UserShow.user_id == user_id,
        Show.start_time >= now
    ).order_by(Show.start_time).all()

    shows_data = []
    shows_attendees = {}
    for user_show in user_shows:
        show = user_show.show
        shows_data.append(show.to_dict())

        # Fetch attendees for the show
        attendees = User.query.join(UserShow).filter(UserShow.show_id == show.id).all()
        attendees_in_group = [user for user in attendees if user.group_id == current_user.group_id]
        shows_attendees[show.id] = [{'id': user.id, 'avatarUrl': f"/profile_pics/{user.profile_image}", 'username': user.username} for user in attendees_in_group]

    return jsonify({'shows': shows_data, 'shows_attendees': shows_attendees})


@show_ns.route('/api/shows')
class ShowListResource(Resource):
    @show_ns.doc('list_shows', params={'date': 'Date in YYYY-MM-DD format', 'id': 'Show ID'})
    @show_ns.marshal_with(shows_attendees_model)
    def get(self):
        return get_shows()

@show_ns.route('/api/my-shows')
class MyShowsResource(Resource):
    @show_ns.doc('get_my_shows')
    @show_ns.marshal_with(my_shows_model)
    def get(self):
        return get_my_shows()

@show_ns.route('/api/show')
class ShowDetailResource(Resource):
    @show_ns.doc('get_show', params={'id': 'Show ID'})
    @show_ns.marshal_with(show_attendees_model)
    def get(self):
        return get_show()  
@show_ns.route('/user-shows')
class UserShowsResource(Resource):
    @show_ns.doc('get_user_shows')
    @show_ns.marshal_with(user_shows_model)
    def get(self):
        return user_shows()  


@show_ns.route('/select-show')
class SelectShowResource(Resource):
    @show_ns.doc('select_show')
    @show_ns.expect(show_ns.model('SelectShowPayload', {
        'showId': fields.Integer(required=True, description='The show ID'),
        'action': fields.String(required=True, description='Action to perform (attend/leave)')
    }))
    def post(self):
        return select_show() 