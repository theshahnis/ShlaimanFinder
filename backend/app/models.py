from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    passcode = db.Column(db.String(4), nullable=True)
    users = db.relationship('User', backref='group', lazy=True)

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

    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

class StaticLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    note = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(150), nullable=True)

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
            'start_time': self.start_time.astimezone(amsterdam_tz).strftime('%Y-%m-%d %H:%M'),
            'end_time': self.end_time.astimezone(amsterdam_tz).strftime('%Y-%m-%d %H:%M'),
            'stage': self.stage
        }

class UserShow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    user = db.relationship('User', backref='user_shows')
    show = db.relationship('Show', backref='user_shows')
