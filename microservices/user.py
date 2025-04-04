from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


app = Flask(__name__)
CORS(app)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/car_service"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

# User model
class User(db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.String(13), primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(256), nullable=False) 


    def __init__(self, user_id, name, email, password):
        self.user_id = user_id
        self.password = password  
        self.email = email
        self.name = name

# API endpoint for user registration
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    
    # Validate input
    if not all(key in data for key in ['email', 'password', 'name']):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409
    
    try:
        # Generate user_id
        user_id = 'user_' + uuid.uuid4().hex[:8]
        
        # Hash password
        hashed_password = generate_password_hash(data['password'])
        
        # Create new user
        new_user = User(
            user_id=user_id,
            name = data['name'],
            email = data['email'],
            password= hashed_password,
        )
        
        # Add to database
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id,
            "name": data['name']
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# API endpoint for user login
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    
    if not all(key in data for key in ['email', 'password']):
        return jsonify({"error": "Missing email or password"}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    # Check if user exists and password is correct
    if user and check_password_hash(user.password, data['password']):
        return jsonify({
            "message": "Login successful",
            "user_id": user.user_id
        }), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

if __name__ == "__main__":
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    # Start Flask app
    app.run(host="0.0.0.0", port=5004, debug=True)