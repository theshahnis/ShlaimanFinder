from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField , TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo,Length
from flask_wtf.file import FileAllowed

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_image = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'gif','jpeg','tiff', 'bmp', 'webp'], 'Images only!')])
    note = TextAreaField('Note')  
    submit = SubmitField('Update')

class JoinGroupForm(FlaskForm):
    passcode = StringField('Group Passcode', validators=[DataRequired(), Length(min=4, max=4)])
    submit = SubmitField('Join Group')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')