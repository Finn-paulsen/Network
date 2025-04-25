import os
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# In-memory database for users
users_db = {}
user_id_counter = 1

class User(UserMixin):
    def __init__(self, username, password):
        global user_id_counter
        self.id = user_id_counter
        user_id_counter += 1
        self.username = username
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def save(self):
        users_db[self.id] = self
        return self
    
    @classmethod
    def get_by_id(cls, user_id):
        return users_db.get(user_id)
    
    @classmethod
    def get_by_username(cls, username):
        for user in users_db.values():
            if user.username == username:
                return user
        return None

def init_db():
    """Initialize the in-memory database with a test user if no users exist"""
    if not users_db:
        # Create a test user if none exists
        test_user = User(username="test", password="password")
        test_user.save()
        print("Initialized database with test user 'test' (password: 'password')")
