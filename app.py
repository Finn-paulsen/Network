import os
import logging
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from forms import LoginForm


# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_dev")

# Configure the SQLAlchemy database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.get_by_id(int(user_id))

# Database setup
def setup_database():
    from models import init_db
    with app.app_context():
        db.create_all()
        init_db()

# --- Login required decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Form-Objekt erstellen

    if form.validate_on_submit():  # Überprüfung der Eingaben
        username = form.username.data
        password = form.password.data

        # Hier kannst du echte User-Überprüfung machen
        if username == 'test' and password == 'password':
            session['user_id'] = 1
            return redirect(url_for('dashboard_page'))
        else:
            return 'Falscher Benutzername oder Passwort!'

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))



@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
