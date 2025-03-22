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
    'user': 'your_username',  # Update with your MySQL username
    'password': 'your_password', # Update with your MySQL password
    'database': 'booking_system' # Update with your database name
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
                    booking_id VARCHAR(50) NOT NULL,
                    user_id VARCHAR(50) NOT NULL,
                    action ENUM('created', 'updated', 'cancelled', 'completed') NOT NULL,
                    timestamp DATETIME NOT NULL,
                    details JSON
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
    required_fields = ['booking_id', 'user_id', 'action']
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
    booking_id = log_data.pop('booking_id')
    user_id = log_data.pop('user_id')
    action = log_data.pop('action')
    
    # Parse timestamp
    timestamp_str = log_data.pop('timestamp')
    try:
        # Try to parse ISO format timestamp
        timestamp = datetime.datetime.fromisoformat(timestamp_str)
    except ValueError:
        # Fallback to current time if parsing fails
        timestamp = datetime.datetime.now()
    
    # Remaining data as details JSON
    details = log_data if log_data else None
    
    # Save to MySQL
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Insert record into database
            insert_query = """
                INSERT INTO booking_logs (booking_id, user_id, action, timestamp, details)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            # Convert details dict to JSON string if it exists
            details_json = None
            if details:
                import json
                details_json = json.dumps(details)
                
            cursor.execute(insert_query, (booking_id, user_id, action, timestamp, details_json))
            connection.commit()
            
            print(f"Booking log saved to MySQL with ID: {cursor.lastrowid}")
            
            # Return success response
            return jsonify({
                "code": 200, 
                "message": "Booking log recorded successfully",
                "data": {
                    "booking_id": booking_id,
                    "user_id": user_id,
                    "action": action,
                    "timestamp": timestamp_str,
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

if __name__ == "__main__":
    # Create table on startup
    create_booking_logs_table()
    
    port = int(os.environ.get("PORT", 5004))
    print(f"Booking Log Service running on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)