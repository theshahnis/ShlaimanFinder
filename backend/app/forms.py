from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, EqualTo,Length
from flask_wtf.file import FileAllowed

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_image = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'gif'])])
    submit = SubmitField('Update')

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class JoinGroupForm(FlaskForm):
    passcode = StringField('Group Passcode', validators=[DataRequired(), Length(min=4, max=4)])
    submit = SubmitField('Join Group')
