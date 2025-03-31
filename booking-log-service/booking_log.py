from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import datetime
import json
from os import environ

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/car_service"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = "user"
    
    user_id = db.Column(db.String(13), primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    
    def json(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "username": self.username,
            "email": self.email
        }

class Car(db.Model):
    __tablename__ = "car_available"
    
    id = db.Column(db.String(13), primary_key=True)
    make = db.Column(db.String(64), nullable=False)
    model = db.Column(db.String(64), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(64), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, default=True)
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    town = db.Column(db.String(50), nullable=False)

class BookingLog(db.Model):
    __tablename__ = "booking_logs"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    car_id = db.Column(db.String(13), db.ForeignKey('car_available.id'), nullable=False)
    booking_status = db.Column(db.Enum('not_started', 'in_progress', 'ended'), nullable=False, default='not_started')
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    payment_status = db.Column(db.Enum('pending', 'paid', 'failed', 'refunded'), nullable=False, default='pending')
    payment_method = db.Column(db.String(50))
    total_amount = db.Column(db.Numeric(10, 2))
    transaction_id = db.Column(db.String(100))
    payment_timestamp = db.Column(db.DateTime)
    details = db.Column(db.JSON)
    
    def __init__(self, booking_id, email, start_time, end_time, contact_number, car_id, 
                 booking_status='not_started', payment_status='pending', payment_method=None, 
                 total_amount=None, transaction_id=None, payment_timestamp=None, details=None):
        self.booking_id = booking_id
        self.email = email
        self.start_time = start_time
        self.end_time = end_time
        self.contact_number = contact_number
        self.car_id = car_id
        self.booking_status = booking_status
        self.timestamp = datetime.datetime.now()
        self.payment_status = payment_status
        self.payment_method = payment_method
        self.total_amount = total_amount
        self.transaction_id = transaction_id
        self.payment_timestamp = payment_timestamp
        self.details = details
    
    def json(self):
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "email": self.email,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "contact_number": self.contact_number,
            "car_id": self.car_id,
            "booking_status": self.booking_status,
            "timestamp": self.timestamp.isoformat(),
            "payment_status": self.payment_status,
            "payment_method": self.payment_method,
            "total_amount": float(self.total_amount) if self.total_amount else None,
            "transaction_id": self.transaction_id,
            "payment_timestamp": self.payment_timestamp.isoformat() if self.payment_timestamp else None,
            "details": self.details
        }

# API Routes
@app.route("/api/booking-log", methods=['POST'])
def record_booking_log():
    # Check if the request contains valid JSON
    if not request.is_json:
        return jsonify({
            "code": 400, 
            "message": "Booking log input should be in JSON."
        }), 400
    
    log_data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'start_time', 'end_time', 'contact_number', 'car_id', 'booking_id']
    for field in required_fields:
        if field not in log_data:
            return jsonify({
                "code": 400,
                "message": f"Missing required field: {field}"
            }), 400
    
    # Check if car exists
    car = db.session.scalar(db.select(Car).filter_by(id=log_data['car_id']))
    if not car:
        return jsonify({
            "code": 404,
            "message": f"Car with ID {log_data['car_id']} not found"
        }), 404
    
    # Validate booking status
    valid_statuses = ['not_started', 'in_progress', 'ended']
    booking_status = log_data.get('booking_status', 'not_started')
    if booking_status not in valid_statuses:
        return jsonify({
            "code": 400,
            "message": f"Invalid booking status. Must be one of: {', '.join(valid_statuses)}"
        }), 400
    
    # Parse start and end times
    try:
        start_time = datetime.datetime.fromisoformat(log_data['start_time'])
        end_time = datetime.datetime.fromisoformat(log_data['end_time'])
    except ValueError:
        return jsonify({
            "code": 400,
            "message": "Invalid start_time or end_time format. Use ISO format."
        }), 400
    
    # Parse payment timestamp if provided
    payment_timestamp = None
    if 'payment_timestamp' in log_data and log_data['payment_timestamp']:
        try:
            payment_timestamp = datetime.datetime.fromisoformat(log_data['payment_timestamp'])
        except ValueError:
            return jsonify({
                "code": 400,
                "message": "Invalid payment_timestamp format. Use ISO format."
            }), 400
    
    # Check if user exists by email
    user = db.session.scalar(db.select(User).filter_by(email=log_data['email']))
    
    # Extract fields for booking log
    booking_id = log_data['booking_id']
    email = log_data['email']
    contact_number = log_data['contact_number']
    car_id = log_data['car_id']
    
    # Payment details (optional)
    payment_status = log_data.get('payment_status', 'pending')
    payment_method = log_data.get('payment_method')
    total_amount = log_data.get('total_amount')
    transaction_id = log_data.get('transaction_id')
    
    # Other details to be stored as JSON
    details = {}
    for key, value in log_data.items():
        if key not in ['booking_id', 'email', 'start_time', 'end_time', 
                      'contact_number', 'car_id', 'booking_status', 
                      'payment_status', 'payment_method', 'total_amount', 
                      'transaction_id', 'payment_timestamp']:
            details[key] = value
    
    # Create new booking log
    new_booking_log = BookingLog(
        booking_id=booking_id,
        email=email,
        start_time=start_time,
        end_time=end_time,
        contact_number=contact_number,
        car_id=car_id,
        booking_status=booking_status,
        payment_status=payment_status,
        payment_method=payment_method,
        total_amount=total_amount,
        transaction_id=transaction_id,
        payment_timestamp=payment_timestamp,
        details=details if details else None
    )
    
    try:
        # Add to database
        db.session.add(new_booking_log)
        db.session.commit()
        
        # Enrich response with user data if available
        response_data = new_booking_log.json()
        if user:
            response_data["user"] = user.json()
        
        return jsonify({
            "code": 200,
            "message": "Booking log recorded successfully",
            "data": response_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"Failed to save booking log to database: {str(e)}"
        }), 500

@app.route("/api/booking-logs/<string:email>", methods=['GET'])
def get_user_booking_logs(email):
    """Retrieve booking logs for a specific user by email"""
    
    try:
        # Find user by email
        user = db.session.scalar(db.select(User).filter_by(email=email))
        
        # Get all booking logs for the email
        booking_logs = db.session.scalars(
            db.select(BookingLog).filter_by(email=email).order_by(BookingLog.timestamp.desc())
        ).all()
        
        if booking_logs:
            logs_json = [log.json() for log in booking_logs]
            
            # Include user data if available
            response_data = {"booking_logs": logs_json}
            if user:
                response_data["user"] = user.json()
            
            return jsonify({
                "code": 200,
                "message": "Booking logs retrieved successfully",
                "data": response_data
            }), 200
        else:
            return jsonify({
                "code": 404, 
                "message": f"No booking logs found for email: {email}"
            }), 404
    
    except Exception as e:
        print(f"Error retrieving booking logs: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"Failed to retrieve booking logs: {str(e)}"
        }), 500

@app.route("/api/booking-logs/booking/<string:booking_id>", methods=['GET'])
def get_booking_by_id(booking_id):
    """Retrieve a specific booking log by booking_id"""
    
    try:
        booking = db.session.scalar(db.select(BookingLog).filter_by(booking_id=booking_id))
        
        if booking:
            # Get user info if available
            user = db.session.scalar(db.select(User).filter_by(email=booking.email))
            
            response_data = booking.json()
            if user:
                response_data["user"] = user.json()
            
            return jsonify({
                "code": 200,
                "message": "Booking retrieved successfully",
                "data": response_data
            }), 200
        else:
            return jsonify({
                "code": 404,
                "message": f"No booking found with booking_id: {booking_id}"
            }), 404
    
    except Exception as e:
        print(f"Error retrieving booking: {str(e)}")
        return jsonify({
            "code": 500, 
            "message": f"Failed to retrieve booking: {str(e)}"
        }), 500

@app.route("/api/booking-logs/<string:booking_id>/status", methods=['PUT'])
def update_booking_status(booking_id):
    """Update the status of a booking"""
    
    if not request.is_json:
        return jsonify({
            "code": 400,
            "message": "Input should be in JSON."
        }), 400
    
    data = request.get_json()
    if 'booking_status' not in data:
        return jsonify({
            "code": 400, 
            "message": "Missing 'booking_status' field in request."
        }), 400
    
    # Validate booking status
    valid_statuses = ['not_started', 'in_progress', 'ended']
    if data['booking_status'] not in valid_statuses:
        return jsonify({
            "code": 400,
            "message": f"Invalid booking status. Must be one of: {', '.join(valid_statuses)}"
        }), 400
    
    try:
        booking = db.session.scalar(db.select(BookingLog).filter_by(booking_id=booking_id))
        
        if not booking:
            return jsonify({
                "code": 404,
                "message": f"No booking found with booking_id: {booking_id}"
            }), 404
        
        booking.booking_status = data['booking_status']
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": "Booking status updated successfully",
            "data": booking.json()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Error updating booking status: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"Failed to update booking status: {str(e)}"
        }), 500

@app.route("/api/booking-logs/<string:booking_id>/payment", methods=['PUT'])
def update_payment_info(booking_id):
    """Update payment information for a booking"""
    
    if not request.is_json:
        return jsonify({
            "code": 400,
            "message": "Input should be in JSON."
        }), 400
    
    data = request.get_json()
    
    try:
        booking = db.session.scalar(db.select(BookingLog).filter_by(booking_id=booking_id))
        
        if not booking:
            return jsonify({
                "code": 404,
                "message": f"No booking found with booking_id: {booking_id}"
            }), 404
        
        # Update payment fields if provided
        if 'payment_status' in data:
            valid_statuses = ['pending', 'paid', 'failed', 'refunded']
            if data['payment_status'] not in valid_statuses:
                return jsonify({
                    "code": 400,
                    "message": f"Invalid payment status. Must be one of: {', '.join(valid_statuses)}"
                }), 400
            booking.payment_status = data['payment_status']
        
        if 'payment_method' in data:
            booking.payment_method = data['payment_method']
        
        if 'total_amount' in data:
            booking.total_amount = data['total_amount']
        
        if 'transaction_id' in data:
            booking.transaction_id = data['transaction_id']
        
        if 'payment_timestamp' in data and data['payment_timestamp']:
            try:
                booking.payment_timestamp = datetime.datetime.fromisoformat(data['payment_timestamp'])
            except ValueError:
                return jsonify({
                    "code": 400,
                    "message": "Invalid payment_timestamp format. Use ISO format."
                }), 400
        
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": "Payment information updated successfully",
            "data": booking.json()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Error updating payment information: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"Failed to update payment information: {str(e)}"
        }), 500

if __name__ == "__main__":
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    port = int(environ.get("PORT", 5004))
    print(f"Booking Log Service running on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)