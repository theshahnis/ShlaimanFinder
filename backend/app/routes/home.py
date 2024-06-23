from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request, url_for, current_app
from flask_login import login_required, current_user
from ..models import Location, MeetingPoint, StaticLocation, User, Group, Hotel, UserHotel
from app.extensions import db
import os
from .api import token_or_login_required

home_bp = Blueprint('home_bp', __name__)


@home_bp.route('/home_data', methods=['GET'])
@token_or_login_required
def get_home_data():
    # Active Users
    thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
    active_users = User.query.join(Location).filter(Location.timestamp >= thirty_minutes_ago).count()

    # Upcoming Events
    upcoming_shows = (
        db.session.query(Show)
        .join(UserShow)
        .filter(UserShow.user_id == current_user.id, Show.start_time > datetime.utcnow() - timedelta(minutes=30))
        .order_by(Show.start_time)
        .limit(3)
        .all()
    )

    # Featured Locations (User's Hotel)
    user_hotel = (
        db.session.query(Hotel)
        .join(Hotel.users)
        .filter(User.id == current_user.id)
        .first()
    )

    upcoming_shows_data = [
        {
            "name": show.name,
            "start_time": show.start_time.isoformat(),
            "end_time": show.end_time.isoformat()
        } for show in upcoming_shows
    ]

    hotel_data = None
    if user_hotel:
        hotel_data = {
            "name": user_hotel.name,
            "latitude": user_hotel.latitude,
            "longitude": user_hotel.longitude,
            "start_date": user_hotel.start_date.isoformat(),
            "end_date": user_hotel.end_date.isoformat()
        }

    return jsonify({
        "active_users_count": active_users,
        "upcoming_shows": upcoming_shows_data,
        "featured_hotel": hotel_data
    })
