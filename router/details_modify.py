from flask import Blueprint, request, jsonify
from models.schema import User
from extension import db
from werkzeug.security import generate_password_hash
from datetime import datetime
import pytz


detail_register_bp = Blueprint('detail_register_bp', __name__, url_prefix='/api')

def is_valid_phone(phone):
    return isinstance(phone, str) and phone.isdigit() and 10 <= len(phone) <= 15

def is_valid_name(name):
    return isinstance(name, str) and all(x.isalpha() or x.isspace() for x in name)

def current_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

@detail_register_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return " ", 200

    data = request.get_json()
    full_name = data.get('full_name')
    login_method = data.get('login_method')  # 'google' or 'email'

    if not full_name or not is_valid_name(full_name):
        return jsonify({"error": "Invalid or missing full name"}), 400

    if login_method not in ['google', 'email']:
        return jsonify({"error": "Missing or invalid login_method"}), 400

    created_at = current_ist_time()
    updated_at = created_at

    if login_method == 'google':
        google_id = data.get('google_id')
        if not google_id:
            return jsonify({"error": "'google_id' is required for Google login"}), 400

        existing = User.query.filter_by(google_id=google_id).first()
        if existing:
            return jsonify({"message": "User already exists", "user_id": existing.id}), 200
        
        profile_picture = data.get('profile_picture')

        user = User(
            full_name=full_name,
            google_id=google_id,
            profile_picture=profile_picture,
            login_method='google',
            created_at=created_at,
            updated_at=updated_at
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully", "user_id": user.id}), 201

    if login_method == 'email':
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')

        if not email or not password or not phone or not full_name:
            return jsonify({"error": "Full name, email, password, and phone are required for Email login"}), 400
        if not is_valid_phone(phone):
            return jsonify({"error": "Invalid phone number format"}), 400

        existing = User.query.filter_by(email=email).first()
        if existing:
            return jsonify({"error": "Email already registered"}), 409

        hashed_password = generate_password_hash(password)

        dob = None
        if data.get('dob'):
            try:
                dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid date of birth format. Use YYYY-MM-DD."}), 400

        user = User(
            full_name=full_name,
            email=email,
            password=hashed_password,
            phone=phone,
            state=data.get('state'),
            gender=data.get('gender'),
            qualification=data.get('qualification'),
            marital_status=data.get('marital_status'),
            dob=dob,
            login_method='email',
            created_at=created_at,
            updated_at=updated_at
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully", "user_id": user.id}), 201

@detail_register_bp.route('/register/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    allowed_fields = ['full_name', 'email', 'phone', 'state', 'gender', 'qualification', 'marital_status', 'dob', 'profile_picture']

    for field in allowed_fields:
        if field in data:
            if field == 'dob' and data.get('dob'):
                try:
                    setattr(user, 'dob', datetime.strptime(data['dob'], '%Y-%m-%d').date())
                except ValueError:
                    return jsonify({"error": "Invalid date format for dob. Use YYYY-MM-DD."}), 400
            else:
                setattr(user, field, data[field])

    user.updated_at = datetime.utcnow()

    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Update failed', 'details': str(e)}), 500
