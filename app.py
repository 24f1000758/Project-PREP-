import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta

# Import your application components
from extension import db, register_oauth 
from router import register_routes 

# It's best practice to load environment variables at the very top
load_dotenv()

def create_app():
    """
    Application factory pattern. This makes the app more modular and testable.
    """
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))

    # --- Configuration ---
    # 1. CORRECTED: Load SECRET_KEY from environment variables for security.
    #    Never hardcode secrets in your code.
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a-default-fallback-key-for-dev')

    # 2. Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data_file.sqlite3')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 3. Session cookie settings - FIXED FOR OAUTH
    app.config.update(
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,  # Set to True in production if using HTTPS
        SESSION_COOKIE_HTTPONLY=True,  # Added for security
        SESSION_PERMANENT=False,  # Added to prevent session expiry issues
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),  # Added session timeout
        SESSION_TYPE='filesystem'  # Added explicit session type
    )

    # 4. File upload configuration
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # --- JWT Configuration ---
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=10)

    # --- Initialize Extensions ---
    db.init_app(app)
    register_oauth(app)
    JWTManager(app)

    # --- CORS Configuration - UPDATED FOR OAUTH ---
    CORS(
        app,
        resources={r"/api/*": {
            "origins": [
                "http://localhost:5173",
                "http://localhost:3000",  # Added common React dev port
                r"https://.*\.trycloudflare\.com"  # Regex for any subdomain
            ]
        }},
        supports_credentials=True,  # CRITICAL for OAuth sessions
        allow_headers=["Content-Type", "Authorization", "Cookie"],  # Added Cookie header
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        expose_headers=["Set-Cookie"]  # Added to expose cookie headers
    )

    # --- Register Blueprints ---
    register_routes(app)
    
    return app

app = create_app()
with app.app_context():
    db.create_all()
if __name__ == "__main__":
        # This is fine for development, but for production,
        # consider using a migration tool like Flask-Migrate.
    app.run(host="0.0.0.0", port=5000, debug=False)  # Changed to debug=True for development