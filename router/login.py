from flask import Blueprint, request, jsonify, url_for, redirect
from models.schema import User
from extension import db, oauth
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import pytz
import jwt
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask import session
from flask import session, request, jsonify, redirect, url_for
from flask_jwt_extended import create_access_token
import logging

login_bp = Blueprint('login_bp', __name__, url_prefix='/api')

def is_valid_phone(phone):
    return isinstance(phone, str) and phone.isdigit() and 10 <= len(phone) <= 15

def is_valid_name(name):
    return isinstance(name, str) and all(x.isalpha() or x.isspace() for x in name)

def current_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

# ********************************* Login Route ***********************************
#                   Handles both email & passwrod for user and admin
# **********************************************************************************
admin_emails = 'gaurav.admin@prep.in'
admin_password = 'Admin@123'
@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    print(f"Attempting login for email: '{email}'") # Add this line
    print(f"Attempting login with password: '{password}'") # Add this line
    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    if email == admin_emails and password == admin_password:
        access_token = create_access_token(identity='admin')
        return jsonify({
            'message': 'Admin login successful', 
            'access_token': access_token,
            'role':'admin'
        }), 200

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email or password.'}), 401
    
    access_token = create_access_token(identity=str(user.id))

    # Return user details along with token
    user_data = {
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'profile_picture': user.profile_picture or '',  # typically empty for email users
        'qualification': user.qualification,
        'gender': user.gender,
        'state': user.state,
        'dob': user.dob.isoformat() if user.dob else '',
        'login_method': user.login_method,
        'phone': user.phone,
        'married': user.marital_status
    }

    return jsonify({
        'message': 'Login successful', 
        'user': user_data, 
        'access_token': access_token,
        'role':'user'
    }), 200


@login_bp.route('/register', methods=['POST', 'OPTIONS'])
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


@login_bp.route('/google/login')
def google_login():
    # Clear any existing session to start fresh
    session.clear()
    
    # Add debugging
    print(f"=== GOOGLE LOGIN START ===")
    print(f"Session before redirect: {dict(session)}")
    print(f"Session ID: {session.get('_id', 'No session ID')}")
    
    redirect_uri = url_for('login_bp.google_callback', _external=True)
    print(f"Redirect URI: {redirect_uri}")
    
    # Ensure session is saved before redirect
    session.permanent = True
    
    return oauth.google.authorize_redirect(redirect_uri)

# Replace your google_callback function with this cleaned version:
@login_bp.route('/google/callback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo') or oauth.google.get('userinfo').json()
    except Exception as e:
        if "mismatching_state" in str(e).lower():
            code = request.args.get('code')
            if not code:
                return jsonify({"error": "No authorization code received"}), 400
            
            try:
                import requests
                redirect_uri = url_for('login_bp.google_callback', _external=True)
                
                token_data = {
                    'client_id': oauth.google.client_id,
                    'client_secret': oauth.google.client_secret,
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': redirect_uri
                }
                
                response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
                
                if response.status_code == 200:
                    token = response.json()
                    access_token = token.get('access_token')
                    user_info_response = requests.get(
                        'https://www.googleapis.com/oauth2/v2/userinfo',
                        headers={'Authorization': f'Bearer {access_token}'}
                    )
                    
                    if user_info_response.status_code == 200:
                        user_info = user_info_response.json()
                    else:
                        return jsonify({"error": "Failed to get user information"}), 400
                else:
                    return jsonify({"error": "Failed to exchange authorization code"}), 400
            except Exception as manual_error:
                return jsonify({"error": "Authentication failed"}), 400
        else:
            return jsonify({"error": f"OAuth error: {str(e)}"}), 400

    google_id = user_info.get('sub') or user_info.get('id')
    if google_id is None:
        return jsonify({"error": "Google user ID not found in response"}), 400

    full_name = user_info.get('name')
    email = user_info.get('email')
    profile_picture = user_info.get('picture')

    created_at = current_ist_time()
    updated_at = created_at

    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        user = User(
            google_id=google_id,
            full_name=full_name,
            email=email,
            profile_picture=profile_picture,
            login_method='google',
            created_at=created_at,
            updated_at=updated_at
        )
        db.session.add(user)
        db.session.commit()
    
    jwt_token = create_access_token(identity=str(user.id))
    session['jwt_token'] = jwt_token

    return redirect(f'http://localhost:5173/google-auth-finish?redirect=/dashboard&token={jwt_token}')

@login_bp.route('/user', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_user():
    if request.method == 'OPTIONS':
        return '', 200  # Respond OK to OPTIONS preflight

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_data = {
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'profile_picture': user.profile_picture,
        'qualification': user.qualification,
        'gender': user.gender,
        'state': user.state,
        'dob': user.dob.isoformat() if user.dob else '',
        'login_method': user.login_method,
        'phone': user.phone,
        'married': user.marital_status
    }
    return jsonify(user_data)



@login_bp.route('/google/token', methods=['GET'])
def google_token():
    jwt_token = session.get('jwt_token')
    if not jwt_token:
        return jsonify({"error": "Unauthorized or token not found"}), 401

    return jsonify({
        "access_token": jwt_token,
        "message": "Token retrieval successful"
    })
