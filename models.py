import os
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    access_level = db.Column(db.Integer, default=1)  # 1: Standard, 2: Advanced, 3: Admin
    
    def __init__(self, username, password, access_level=1):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.access_level = access_level
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.get(int(user_id))
    
    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

# Criminal Database Models
class Suspect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    alias = db.Column(db.String(100))
    nationality = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    height = db.Column(db.Float)  # in cm
    weight = db.Column(db.Float)  # in kg
    eye_color = db.Column(db.String(20))
    hair_color = db.Column(db.String(20))
    last_known_location = db.Column(db.String(100))
    threat_level = db.Column(db.Integer, default=1)  # 1-5, with 5 being highest
    status = db.Column(db.String(20), default='Active')  # Active, Captured, Deceased
    photo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    criminal_records = db.relationship('CriminalRecord', backref='suspect', lazy=True)
    wanted_notices = db.relationship('WantedNotice', backref='suspect', lazy=True)
    
    def __repr__(self):
        return f"<Suspect {self.first_name} {self.last_name}>"

class CriminalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    suspect_id = db.Column(db.Integer, db.ForeignKey('suspect.id'), nullable=False)
    crime = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date_committed = db.Column(db.Date)
    location = db.Column(db.String(100))
    jurisdiction = db.Column(db.String(50))  # Country or region
    status = db.Column(db.String(20))  # Alleged, Convicted, Acquitted
    sentence = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CriminalRecord {self.crime}>"

class WantedNotice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    suspect_id = db.Column(db.Integer, db.ForeignKey('suspect.id'), nullable=False)
    notice_type = db.Column(db.String(20), default='Red')  # Red, Yellow, Blue, etc.
    issuing_country = db.Column(db.String(50), nullable=False)
    charge = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    date_issued = db.Column(db.Date, default=datetime.utcnow)
    expiration_date = db.Column(db.Date)
    reward_amount = db.Column(db.Float)
    contact_info = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f"<WantedNotice {self.notice_type} - {self.charge}>"

# Attack Simulation Models
class DDOSTarget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_name = db.Column(db.String(100), nullable=False)
    target_url = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    port = db.Column(db.Integer, default=80)
    protocol = db.Column(db.String(10), default='HTTP')  # HTTP, HTTPS, FTP, etc.
    target_type = db.Column(db.String(20))  # Website, API, Server, etc.
    vulnerability_level = db.Column(db.Integer, default=3)  # 1-5 scale
    country = db.Column(db.String(50))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attack_logs = db.relationship('DDOSAttackLog', backref='target', lazy=True)
    
    def __repr__(self):
        return f"<DDOSTarget {self.target_name}>"

class DDOSAttackLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('ddos_target.id'), nullable=False)
    attack_method = db.Column(db.String(50), nullable=False)  # SYN Flood, UDP Flood, HTTP Flood, etc.
    packets_sent = db.Column(db.Integer, default=0)
    bandwidth_used = db.Column(db.Float, default=0)  # in Mbps
    duration = db.Column(db.Integer, default=0)  # in seconds
    attack_status = db.Column(db.String(20), default='Preparing')  # Preparing, Running, Completed, Failed
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    success_rate = db.Column(db.Float, default=0)  # 0-100%
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f"<DDOSAttackLog {self.attack_method}>"

def init_db():
    """Initialize the database with test data if empty"""
    # Check if any users exist
    if User.query.count() == 0:
        # Create a test user
        test_user = User(username='test', password='password', access_level=3)
        db.session.add(test_user)
        
        # Create some test suspects
        suspects = [
            Suspect(
                first_name='John', 
                last_name='Doe', 
                alias='The Ghost', 
                nationality='USA', 
                date_of_birth=datetime.strptime('1985-03-15', '%Y-%m-%d'), 
                gender='Male',
                height=185, 
                weight=80, 
                eye_color='Blue', 
                hair_color='Brown',
                last_known_location='Berlin, Germany',
                threat_level=4,
                status='Active',
                photo_url='suspect1.jpg'
            ),
            Suspect(
                first_name='Maria', 
                last_name='Schmidt', 
                alias='Black Widow', 
                nationality='Germany', 
                date_of_birth=datetime.strptime('1990-07-22', '%Y-%m-%d'), 
                gender='Female',
                height=170, 
                weight=65, 
                eye_color='Green', 
                hair_color='Black',
                last_known_location='Prague, Czech Republic',
                threat_level=5,
                status='Active',
                photo_url='suspect2.jpg'
            ),
            Suspect(
                first_name='Dmitri', 
                last_name='Petrov', 
                alias='The Programmer', 
                nationality='Russia', 
                date_of_birth=datetime.strptime('1988-11-03', '%Y-%m-%d'), 
                gender='Male',
                height=178, 
                weight=75, 
                eye_color='Brown', 
                hair_color='Brown',
                last_known_location='Unknown',
                threat_level=5,
                status='Active',
                photo_url='suspect3.jpg'
            )
        ]
        
        for suspect in suspects:
            db.session.add(suspect)
        
        # Commit all records to the database
        db.session.commit()
        
        # Add criminal records for the suspects
        criminal_records = [
            CriminalRecord(
                suspect_id=1,
                crime='Cybercrime',
                description='Hacked multiple government databases',
                date_committed=datetime.strptime('2022-05-10', '%Y-%m-%d'),
                location='Washington D.C., USA',
                jurisdiction='USA',
                status='Alleged',
                sentence=None
            ),
            CriminalRecord(
                suspect_id=2,
                crime='Corporate Espionage',
                description='Stole confidential data from tech companies',
                date_committed=datetime.strptime('2023-01-15', '%Y-%m-%d'),
                location='Munich, Germany',
                jurisdiction='Germany',
                status='Convicted',
                sentence='10 years imprisonment (escaped)'
            ),
            CriminalRecord(
                suspect_id=3,
                crime='Ransomware Development',
                description='Created and distributed ransomware affecting hospitals',
                date_committed=datetime.strptime('2022-08-22', '%Y-%m-%d'),
                location='Multiple locations',
                jurisdiction='International',
                status='Alleged',
                sentence=None
            )
        ]
        
        for record in criminal_records:
            db.session.add(record)
        
        # Add wanted notices
        wanted_notices = [
            WantedNotice(
                suspect_id=1,
                notice_type='Red',
                issuing_country='USA',
                charge='Cyber Terrorism',
                details='Wanted for breaching national security databases',
                date_issued=datetime.strptime('2022-06-01', '%Y-%m-%d'),
                expiration_date=None,
                reward_amount=100000,
                contact_info='FBI Cyber Division',
                is_active=True
            ),
            WantedNotice(
                suspect_id=2,
                notice_type='Red',
                issuing_country='Germany',
                charge='Theft of Intellectual Property',
                details='Wanted for stealing proprietary technology',
                date_issued=datetime.strptime('2023-02-10', '%Y-%m-%d'),
                expiration_date=None,
                reward_amount=75000,
                contact_info='Bundeskriminalamt',
                is_active=True
            ),
            WantedNotice(
                suspect_id=3,
                notice_type='Red',
                issuing_country='International',
                charge='Cyber Crime',
                details='Wanted for creating destructive ransomware',
                date_issued=datetime.strptime('2022-09-15', '%Y-%m-%d'),
                expiration_date=None,
                reward_amount=250000,
                contact_info='Interpol Cyber Crime Unit',
                is_active=True
            )
        ]
        
        for notice in wanted_notices:
            db.session.add(notice)
        
        # Add some DDoS targets for simulation
        ddos_targets = [
            DDOSTarget(
                target_name='Test Bank Website',
                target_url='https://testbank.example.com',
                ip_address='192.168.1.100',
                port=443,
                protocol='HTTPS',
                target_type='Website',
                vulnerability_level=2,
                country='Germany',
                created_by=1
            ),
            DDOSTarget(
                target_name='Government Portal',
                target_url='https://gov.example.org',
                ip_address='10.0.0.1',
                port=443,
                protocol='HTTPS',
                target_type='Website',
                vulnerability_level=4,
                country='USA',
                created_by=1
            )
        ]
        
        for target in ddos_targets:
            db.session.add(target)
        
        # Commit all records
        db.session.commit()
        
        print("Initialized database with test user 'test' (password: 'password')")
    else:
        print("Database already contains data, skipping initialization")
