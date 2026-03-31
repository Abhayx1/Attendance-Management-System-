from datetime import datetime
from backend.database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default="Employee") # Admin, Employee
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    embedding_path = db.Column(db.String(255)) # Path to stored face image for DeepFace matching
    
    attendances = db.relationship('Attendance', backref='user', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Present') # Present, Late, Absent

class SecurityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_time = db.Column(db.DateTime, default=datetime.utcnow)
    event_type = db.Column(db.String(50), nullable=False) # e.g. "Spoofing Attempt", "Unknown Face"
    details = db.Column(db.Text)
