#!/usr/bin/env python3

import os
import datetime
import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# MySQL Configuration
DB_CONFIG = {
    'host': 'localhost',      # Update with your MySQL host
    'user': 'root',  # Update with your MySQL username
    'password': '', # Update with your MySQL password
    'database': 'car_service' # Update with your database name
}

def get_db_connection():
    """Create and return a connection to the MySQL database"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def create_booking_logs_table():
    """Create the booking_logs table if it doesn't exist"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS booking_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(50) NOT NULL,
                    user_name VARCHAR(100) NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME NOT NULL,
                    contact_number VARCHAR(20) NOT NULL,
                    email_address VARCHAR(100) NOT NULL,
                    car_id VARCHAR(50) NOT NULL,
                    action ENUM('created', 'updated', 'cancelled', 'completed') NOT NULL,
                    timestamp DATETIME NOT NULL,
                    payment_status ENUM('pending', 'paid', 'failed', 'refunded') NOT NULL DEFAULT 'pending',
                    payment_method VARCHAR(50),
                    total_amount DECIMAL(10, 2),
                    transaction_id VARCHAR(100),
                    payment_timestamp DATETIME,
                    details JSON,
                    FOREIGN KEY (car_id) REFERENCES car_available(id)
                )
            ''')
            connection.commit()
            print("Booking logs table created or already exists")
        except mysql.connector.Error as err:
            print(f"Error creating table: {err}")
        finally:
            cursor.close()
            connection.close()

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
    required_fields = ['user_id', 'user_name', 'start_time', 'end_time', 'contact_number', 'email_address', 'car_id', 'action']
    for field in required_fields:
        if field not in log_data:
            return jsonify({
                "code": 400,
                "message": f"Missing required field: {field}"
            }), 400
    
    # Validate action type
    valid_actions = ['created', 'updated', 'cancelled', 'completed']
    if log_data['action'] not in valid_actions:
        return jsonify({
            "code": 400,
            "message": f"Invalid action. Must be one of: {', '.join(valid_actions)}"
        }), 400
    
    # Add timestamp if not provided
    if 'timestamp' not in log_data:
        log_data['timestamp'] = datetime.datetime.now().isoformat()
    
    # Extract main fields and any additional data
    user_id = log_data.pop('user_id')
    user_name = log_data.pop('user_name')
    start_time = log_data.pop('start_time')
    end_time = log_data.pop('end_time')
    contact_number = log_data.pop('contact_number')
    email_address = log_data.pop('email_address')
    car_id = log_data.pop('car_id')
    action = log_data.pop('action')
    
    # Parse timestamp
    timestamp_str = log_data.pop('timestamp')
    try:
        # Try to parse ISO format timestamp
        timestamp = datetime.datetime.fromisoformat(timestamp_str)
    except ValueError:
        # Fallback to current time if parsing fails
        timestamp = datetime.datetime.now()
    
    # Parse start and end times
    try:
        start_time = datetime.datetime.fromisoformat(start_time)
        end_time = datetime.datetime.fromisoformat(end_time)
    except ValueError:
        return jsonify({
            "code": 400,
            "message": "Invalid start_time or end_time format. Use ISO format."
        }), 400
    
    # Payment details (optional)
    payment_status = log_data.pop('payment_status', 'pending')
    payment_method = log_data.pop('payment_method', None)
    total_amount = log_data.pop('total_amount', None)
    transaction_id = log_data.pop('transaction_id', None)
    payment_timestamp = log_data.pop('payment_timestamp', None)
    
    # Parse payment timestamp if provided
    if payment_timestamp:
        try:
            payment_timestamp = datetime.datetime.fromisoformat(payment_timestamp)
        except ValueError:
            payment_timestamp = None
    
    # Remaining data as details JSON
    details = log_data if log_data else None
    
    # Save to MySQL
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Insert record into database
            insert_query = """
                INSERT INTO booking_logs (
                    user_id, user_name, start_time, end_time, 
                    contact_number, email_address, car_id, 
                    action, timestamp, payment_status, 
                    payment_method, total_amount, transaction_id, 
                    payment_timestamp, details
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Convert details dict to JSON string if it exists
            details_json = None
            if details:
                import json
                details_json = json.dumps(details)
                
            cursor.execute(insert_query, (
                user_id, user_name, start_time, end_time, 
                contact_number, email_address, car_id, 
                action, timestamp, payment_status, 
                payment_method, total_amount, transaction_id, 
                payment_timestamp, details_json
            ))
            connection.commit()
            
            print(f"Booking log saved to MySQL with ID: {cursor.lastrowid}")
            
            # Return success response
            return jsonify({
                "code": 200, 
                "message": "Booking log recorded successfully",
                "data": {
                    "user_id": user_id,
                    "user_name": user_name,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "contact_number": contact_number,
                    "email_address": email_address,
                    "car_id": car_id,
                    "action": action,
                    "timestamp": timestamp_str,
                    "payment_status": payment_status,
                    "payment_method": payment_method,
                    "total_amount": total_amount,
                    "transaction_id": transaction_id,
                    "payment_timestamp": payment_timestamp.isoformat() if payment_timestamp else None,
                    "details": details
                },
                "log_id": cursor.lastrowid
            }), 200
        
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return jsonify({
                "code": 500,
                "message": "Failed to save booking log to database"
            }), 500
        finally:
            cursor.close()
            connection.close()
    else:
        # Database connection failed
        print("Could not connect to database")
        # Store log in console for debugging
        print("Recording a booking log (not saved to database):")
        print(log_data)
        return jsonify({
            "code": 500,
            "message": "Database connection failed, log recorded to console only"
        }), 500

@app.route("/api/booking-logs/<id>", methods=['GET'])
def get_user_booking_logs(user_id):
    """Retrieve booking logs for a specific user"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Retrieve all booking logs for the user
            query = """
                SELECT * FROM booking_logs 
                WHERE user_id = %s 
                ORDER BY timestamp DESC
            """
            cursor.execute(query, (user_id,))
            
            # Fetch all logs
            logs = cursor.fetchall()
            
            # Convert details from JSON string to dict if exists
            for log in logs:
                if log['details']:
                    log['details'] = json.loads(log['details'])
            
            return jsonify({
                "code": 200,
                "message": "Booking logs retrieved successfully",
                "data": logs
            }), 200
        
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return jsonify({
                "code": 500,
                "message": "Failed to retrieve booking logs"
            }), 500
        finally:
            cursor.close()
            connection.close()
    else:
        return jsonify({
            "code": 500,
            "message": "Database connection failed"
        }), 500

if __name__ == "__main__":
    # Create table on startup
    create_booking_logs_table()
    
    port = int(os.environ.get("PORT", 5004))
    print(f"Booking Log Service running on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)