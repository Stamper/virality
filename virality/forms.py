from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, FileField
from wtforms.validators import Email, DataRequired
from wtforms.widgets import TextArea


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class SignUpForm(LoginForm):
    invite = HiddenField('invite')
    password2 = PasswordField('Re-enter password', validators=[DataRequired()])


class ProfileForm(FlaskForm):
    description = StringField('Description', widget=TextArea())
    image = FileField('Image')
