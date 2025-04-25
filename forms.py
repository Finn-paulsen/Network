from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class NetworkScanForm(FlaskForm):
    target = StringField('Target IP/Range', validators=[DataRequired()])
    submit = SubmitField('Scan')

class TerminalCommandForm(FlaskForm):
    command = TextAreaField('Command', validators=[DataRequired()])
    submit = SubmitField('Execute')
    
class FirewallRuleForm(FlaskForm):
    source_ip = StringField('Source IP', validators=[DataRequired()])
    destination_ip = StringField('Destination IP', validators=[DataRequired()])
    action = StringField('Action (allow/deny)', validators=[DataRequired()])
    submit = SubmitField('Add Rule')
