import os
import sys
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

sys.path.insert(0, os.getcwd())

from backend.database import db
from backend.models import User, Attendance, SecurityLog
from utils.face_recognition_utils import register_face, recognize_face

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

# Database Configuration
DB_DIR = os.path.join(os.getcwd(), 'database')
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(DB_DIR, 'attendance.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables upon startup
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/dashboard')
def dashboard():
    return app.send_static_file('dashboard.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    employee_id = data.get('employee_id')
    name = data.get('name')
    image_base64 = data.get('image')

    if not all([employee_id, name, image_base64]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    # Ensure user does not already exist
    existing_user = User.query.filter_by(employee_id=employee_id).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Employee ID already exists'}), 400

    # Register face using utility
    res = register_face(employee_id, image_base64)
    if not res['success']:
        return jsonify(res), 400

    # Save to database
    new_user = User(
        employee_id=employee_id,
        name=name,
        role="Employee",
        embedding_path=res['path']
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'User registered successfully'})

@app.route('/api/recognize', methods=['POST'])
def api_recognize():
    data = request.json
    image_base64 = data.get('image')

    if not image_base64:
        return jsonify({'success': False, 'message': 'Missing image data'}), 400

    res = recognize_face(image_base64)

    # Log spoofing attempt
    if res.get('is_spoof'):
        log_entry = SecurityLog(event_type='Spoofing Attempt', details=res.get('message', 'Potential static image or non-live face.'))
        db.session.add(log_entry)
        db.session.commit()
        return jsonify(res), 403

    if not res['success']:
        return jsonify(res), 404

    # Recognize success -> Mark Attendance
    employee_id = res['identity']
    user = User.query.filter_by(employee_id=employee_id).first()
    
    if not user:
        return jsonify({'success': False, 'message': 'Recognized face not found in database'}), 404

    # Check for duplicate check-in within last 10 minutes
    ten_mins_ago = datetime.utcnow() - timedelta(minutes=10)
    today = datetime.utcnow().date()
    
    recent_attendance = Attendance.query.filter(
        Attendance.user_id == user.id,
        Attendance.date == today,
        Attendance.check_in_time >= ten_mins_ago
    ).first()

    if recent_attendance:
        return jsonify({'success': True, 'identity': employee_id, 'name': user.name, 'message': 'Already checked-in recently, skipping duplicate entry.'})

    # Mark general Attendance logic - assume 'Present' if marked at all. Could add Late logic.
    new_record = Attendance(
        user_id=user.id,
        date=today,
        status='Present'
    )
    db.session.add(new_record)
    db.session.commit()

    return jsonify({'success': True, 'identity': employee_id, 'name': user.name, 'message': 'Attendance marked successfully.'})

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    """Admin endpoint to get records"""
    records = Attendance.query.order_by(Attendance.check_in_time.desc()).limit(100).all()
    results = []
    for r in records:
        results.append({
            'date': r.date.strftime('%Y-%m-%d'),
            'time': r.check_in_time.strftime('%H:%M:%S'),
            'name': r.user.name,
            'employee_id': r.user.employee_id,
            'status': r.status
        })
    return jsonify({'success': True, 'records': results})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Admin Dashboard Stats"""
    today = datetime.utcnow().date()
    total_users = User.query.count()
    present_today = Attendance.query.filter_by(date=today).count()
    spoof_attempts = SecurityLog.query.filter_by(event_type='Spoofing Attempt').count()

    attendance_percentage = (present_today / total_users * 100) if total_users > 0 else 0

    return jsonify({
        'success': True,
        'total_users': total_users,
        'present_today': present_today,
        'absent_today': total_users - present_today,
        'attendance_percentage': round(attendance_percentage, 2),
        'spoof_attempts': spoof_attempts
    })

if __name__ == '__main__':
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
