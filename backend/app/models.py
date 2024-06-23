from .extensions import db
from flask_login import UserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,timedelta
import pytz,jwt


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    passcode = db.Column(db.String(4), nullable=True)
    users = db.relationship('User', backref='group', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'passcode': self.passcode,
            'users': [user.to_dict() for user in self.users]
        }

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    superuser = db.Column(db.Boolean, default=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)
    profile_image = db.Column(db.String(150), nullable=True)
    passcode_attempts = db.Column(db.Integer, default=0, nullable=True)
    note = db.Column(db.Text, nullable=True)
    api_token = db.Column(db.String(512), unique=True, nullable=True) 
    phone_number = db.Column(db.String(20), nullable=True)
    

    

    def generate_api_token(self, secret_key):
        token_data = {
            'user_id': self.id,
            'sub': self.id,
            'exp': (datetime.utcnow() + timedelta(days=7)).timestamp()
        }
        token = jwt.encode(token_data, secret_key, algorithm='HS256')
        self.api_token = token
        db.session.commit()
        return token

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'superuser': self.superuser,
            'group': self.group.name if self.group else None,
            'profile_image': self.profile_image,
            'note': self.note,
            'phone_number': self.phone_number
        }
    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref=db.backref('locations', lazy=True))

class MeetingPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    username = db.Column(db.String(150), nullable=False)
    note = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(150), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    group = db.relationship('Group', backref=db.backref('meeting_points', lazy=True))
    duration = db.Column(db.Integer, default=3, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'username': self.username,
            'note': self.note,
            'image': self.image,
            'group_id': self.group_id,
            'duration': self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class StaticLocation(db.Model):
    __tablename__ = 'static_location'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    note = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(150), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'note': self.note,
            'image': self.image
        }

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    stage = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        amsterdam_tz = pytz.timezone('Europe/Amsterdam')
        return {
            'id': self.id,
            'name': self.name,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M'),
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M'),
            'stage': self.stage
        }

class UserShow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    user = db.relationship('User', backref='user_shows')
    show = db.relationship('Show', backref='user_shows')


class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    users = db.relationship('User', secondary='user_hotel', backref='hotels')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'users': [user.username for user in self.users]
        }

class UserHotel(db.Model):
    __tablename__ = 'user_hotel'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), primary_key=True)