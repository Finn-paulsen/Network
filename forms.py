from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField, FileField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Optional, NumberRange, URL

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

class BruteForceForm(FlaskForm):
    target_type = SelectField('Target Type', choices=[
        ('password', 'Password'),
        ('hash', 'Hash'),
        ('pin', 'PIN Code')
    ], validators=[DataRequired()])
    target_value = StringField('Target Value', validators=[DataRequired()])
    character_set = SelectField('Character Set', choices=[
        ('numeric', 'Numeric (0-9)'),
        ('alpha', 'Alphabetic (a-z)'),
        ('alphanumeric', 'Alphanumeric (a-z, 0-9)'),
        ('full', 'Full Set (a-z, A-Z, 0-9, symbols)')
    ], validators=[DataRequired()])
    min_length = IntegerField('Minimum Length', validators=[DataRequired(), NumberRange(min=1, max=6)], default=1)
    max_length = IntegerField('Maximum Length', validators=[DataRequired(), NumberRange(min=1, max=6)], default=4)
    submit = SubmitField('Start Simulation')

class ExploitScannerForm(FlaskForm):
    target_url = StringField('Target URL/IP', validators=[DataRequired()])
    scan_type = SelectField('Scan Type', choices=[
        ('basic', 'Basic Vulnerability Scan'),
        ('advanced', 'Advanced Vulnerability Scan'),
        ('dos', 'DoS Vulnerability Check'),
        ('sqli', 'SQL Injection Test'),
        ('xss', 'XSS Vulnerability Test')
    ], validators=[DataRequired()])
    intensity = SelectField('Scan Intensity', choices=[
        ('low', 'Low (Educational)'),
        ('medium', 'Medium (Simulated)'),
        ('high', 'High (Simulated)')
    ], validators=[DataRequired()])
    submit = SubmitField('Scan for Vulnerabilities')

class MalwareSimulatorForm(FlaskForm):
    target_system = StringField('Target System', validators=[DataRequired()])
    malware_type = SelectField('Simulation Type', choices=[
        ('ransomware', 'Ransomware (Simulated)'),
        ('trojan', 'Trojan (Simulated)'),
        ('virus', 'Virus (Simulated)'),
        ('worm', 'Worm (Simulated)'),
        ('rootkit', 'Rootkit (Simulated)')
    ], validators=[DataRequired()])
    simulation_only = BooleanField('Simulation Only (No actual files created)', default=True)
    propagation = SelectField('Propagation Method', choices=[
        ('email', 'Email Attachment (Simulated)'),
        ('network', 'Network Spread (Simulated)'),
        ('usb', 'USB Drive (Simulated)'),
        ('download', 'Malicious Download (Simulated)')
    ], validators=[DataRequired()])
    submit = SubmitField('Run Simulation')
