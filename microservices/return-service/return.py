import sys
import os
import pika
import json
import base64
import requests
from flask_cors import CORS
from flask import redirect, url_for
from flask import Flask, jsonify, request

# Add project root to path for importing custom modules
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import amqp_lib as amqp

app = Flask(__name__)
CORS(app)

# Microservice URLs
PAYMENTURL = "http://payment_service:5008/api/v1/pay-fine" 
VIOLATIONLOGURL = "https://personal-qednlunm.outsystemscloud.com/violationlog/rest/violationlog/createViolationLog"
UPLOADURL = "http://aiprocessing:9000/api/upload"
REKOGNITIONURL = "http://aiprocessing:9000/api/rekognition"
BOOKINGLOGURL = "http://booking_log:5006/api/booking/{}"
GETALLBOOKINGURL = "http://booking_log:5006/api/booking-logs/user/{}"
ERROR_HANDLER_URL = "http://error_handler:5005/api/log-error"


# # RabbitMQ Configuration
rabbit_host = "host.docker.internal"
rabbit_port = 5672
exchange_name = "smartcar_topic"
exchange_type = "topic"
connection = None 
channel = None

def report_error_to_handler(status_code, error_type, message):
    """Send error details to the error handling microservice."""
    error_payload = {
        "status_code": status_code,
        "error_type": error_type,
        "message": message
    }
    try:
        response = requests.post(ERROR_HANDLER_URL, json=error_payload)
        print(f"Error handler response: {response.status_code}, {response.text}")
        return response.json()  # Log or print response if needed
    except Exception as e:
        print(f"Failed to send error to handler: {str(e)}")


def connectAMQP():
    global connection
    global channel

    print("Connecting to AMQP broker...")
    try:
        connection, channel = amqp.connect(
            hostname=rabbit_host,
            port=rabbit_port,
            exchange_name=exchange_name,
            exchange_type=exchange_type,
        )
    except Exception as exception:
        report_error_to_handler(500, "RabbitMQ Connection Error", str(exception))
        print(f"Unable to connect to RabbitMQ.\n{exception=}\n")
        exit(1)  # terminate

def publish_notification(booking_id, phone_number, is_defected):
    """
    publishes a message to the notification queue on rabbitmq broker
    message is a json-formatted string with booking_id, phone_number and message

    returns a json object with status code 
    """
    try:
        if not phone_number:
            report_error_to_handler(500, "Notification Error", "Phone number missing in booking log")
            return jsonify({'error': 'Phone number missing in booking log'}), 500
            
        if channel is None:
            report_error_to_handler(500, "AMQP Error", "AMQP channel not available")
            return jsonify({'error': 'AMQP channel not available'}), 500
            
        if is_defected:
            message = "We have detected defects in your most recent closed booking. Please make payment via the app or contact support if you wish to seek further clarification"
        else:
            message = "Your vehicle return process is complete."
        channel.basic_publish(
            exchange=exchange_name, 
            routing_key="order.notif", 
            body=json.dumps({
                'booking_id': booking_id,
                'phone_number': phone_number,
                'message': message
            })
        )
        return jsonify({'message': 'Notification sent successfully'})

    except pika.exceptions.UnroutableError:
        report_error_to_handler(500, "Notification Error", "Failed to send notification")
        return jsonify({'error': 'Failed to send notification'}), 500
    except Exception as e:
        report_error_to_handler(500, "Notification Error", str(e))
        return jsonify({'error': 'Failed to send notification', 'details': str(e)}), 500

@app.route('/api/get-all-bookings/<user_id>', methods=["GET"])
def get_bookings(user_id):  # <-- Accept user_id here

    response = requests.get(GETALLBOOKINGURL.format(user_id))

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        report_error_to_handler(response.status_code, "Failed to fetch bookings", "error: Failed to fetch bookings")
        return jsonify({"error": "Failed to fetch bookings"}), response.status_code
  

@app.route('/api/return-vehicle', methods=['POST'])
def return_vehicle():
    try:
        booking_id = request.form.get('booking_id')
        files = request.files.getlist('images')

        if not booking_id or not files:
            report_error_to_handler(400, "Bad Request", "Missing booking_id or images")
            return jsonify({'error': 'Missing booking_id or images'}), 400

        images_data = [
            {
                "buffer": base64.b64encode(file.read()).decode('utf-8'),
                "mimetype": file.mimetype,
                "originalname": file.filename
            }
            for file in files
        ]

        payload = {
            "booking_id": booking_id,
            "images": images_data
        }

        # Step 1: Get booking info
        booking_response = requests.get(BOOKINGLOGURL.format(booking_id))
        if booking_response.status_code == 404:
            report_error_to_handler(404, "Not Found", f"Booking ID {booking_id} not found")
            return jsonify({'error': 'Booking not found'}), 404
        elif booking_response.status_code != 200:
            report_error_to_handler(500, "Booking Retrieval Error", f"Error retrieving booking logs: {booking_response.text}")
            return jsonify({'error': 'Error retrieving booking logs', 'details': booking_response.text}), 500

        booking_data = booking_response.json()
        contact_number = booking_data["data"]["contact_number"]

        # Step 2: Upload images
        upload_response = requests.post(UPLOADURL, json=payload)
        if upload_response.status_code != 200:
            report_error_to_handler(500, "Failed to upload images", {upload_response.text})
            return jsonify({'error': 'Failed to upload images', 'details': upload_response.text}), 500

        upload_data = upload_response.json()

        # # Step 3: Run Rekognition
        rekognition_response = requests.post(REKOGNITIONURL, json=upload_data)
        if rekognition_response.status_code != 200:
            report_error_to_handler(500, "Error processing images", {rekognition_response.text})
            return jsonify({'error': 'Error processing images', 'details': rekognition_response.text}), 500

        rekognition_data = rekognition_response.json()
        defect_count = rekognition_data.get('defect_count', 0)

        defect_count = 1

        # print(defect_count)
        # print(booking_id)

        if defect_count > 0:
            # Step 4: Log violation
            response = requests.post(VIOLATIONLOGURL, json={'booking_id': booking_id, 'defect_count': defect_count})
            if response.status_code != 200:
                report_error_to_handler(500, "Violation Log Error", f"Error logging violations: {response.text}")
                return jsonify({'error': 'Error logging violations', 'details': response.text}), 500

            data = response.json()
            log_data = data.get("GetAllViolationLog", {}).get("GetAllViolationLog", {})

            violation_booking_id = log_data.get("Id")
            total_charge = log_data.get("total_charge")

            if violation_booking_id is None or total_charge is None:
                report_error_to_handler(500, "Violation Data Error", "Missing booking ID or total charge in violation response")
                return jsonify({'error': 'Missing booking ID or total charge in violation response'}), 500

            # Step 5: Send Notification
            notification_response = publish_notification(booking_id,contact_number, is_defected=True)
            # print(json.dumps(notification_response))

            # Step 6: Payment
            try:
                # Check if the notification was sent successfully
                if notification_response.status_code == 200:
                    payment_response = requests.post(PAYMENTURL, json={'amount': total_charge})
                    
                    # If payment is successful
                    if payment_response.status_code == 200:
                        # Use the static HTML file path for the redirect
                        redirect_url = './fines-checkout.html'  # Adjust according to the actual path of your HTML file
                        
                        # Return the response with redirect URL and payment details
                        return jsonify({
                            'message': 'Vehicle return processed with violations',
                            'amount': total_charge,
                            'redirect_url': redirect_url,  # Add the redirect URL in the response
                        }), 200
                    else:
                        # If payment failed
                        report_error_to_handler(500, "Payment Processing Error", f"Failed to process payment: {payment_response.text}")
                        return jsonify({'error': 'Failed to process payment', 'details': payment_response.text}), 500

            except Exception as e:
                # Handle other exceptions if necessary
                report_error_to_handler(500, "Internal Server Error", str(e))
                return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

            except Exception as e:
                # Handling errors in payment processing
                report_error_to_handler(500, "Internal Server Error", str(e))
                return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

        # No violations
        publish_notification(booking_id,contact_number, is_defected=False)
        return jsonify({'message': 'no-violations'}), 200

    except Exception as e:
        report_error_to_handler(500, "Internal Server Error", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


if __name__ == '__main__':
    connectAMQP()
    app.run(debug=True, host='0.0.0.0', port=5011)
