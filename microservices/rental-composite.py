from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import datetime
import pika
import json
from apscheduler.schedulers.background import BackgroundScheduler
import amqp_lib as amqp

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Create a scheduler for handling timed car availability updates
scheduler = BackgroundScheduler()
scheduler.start()

#For use with Docker
CAR_AVAILABILITY_SERVICE_URL = "http://car_available:5000"  
BOOKING_LOG_SERVICE_URL = "http://booking_log:5006/api" 
PAYMENT_SERVICE_URL = "http://payment_service:5008/api/v1/payments" 
ERROR_HANDLER_URL = "http://error_handler:5005/api/log-error"

# For local testing
# CAR_AVAILABILITY_SERVICE_URL = "http://localhost:5000"
# BOOKING_LOG_SERVICE_URL = "http://127.0.0.1:5006/api"

# RabbitMQ Configuration
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
        return response.json()
    except Exception as e:
        print(f"Failed to send error to handler: {str(e)}")

def connectAMQP():
    global connection
    global channel

    print("  Connecting to AMQP broker...")
    try:
        connection, channel = amqp.connect(
                hostname=rabbit_host,
                port=rabbit_port,
                exchange_name=exchange_name,
                exchange_type=exchange_type,
        )
    except Exception as exception:
        report_error_to_handler(500, "RabbitMQ Connection Error", str(exception))
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
        exit(1) # terminate

# #########################################
# # Update car availability based on time #
# #########################################
def get_booking_details(booking_id):
    """
    Get booking details from the booking log service by booking ID
    
    Args:
        booking_id: ID of the booking to retrieve
    
    Returns:
        Dictionary containing booking details or None if not found
    """
    url = f"{BOOKING_LOG_SERVICE_URL}/booking/{booking_id}"
    #http://127.0.0.1:5006/api/booking/booking-1744091289964-nbnu22di6
    
    try:
        logger.info(f"Fetching booking details for ID: {booking_id}")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            # Extract the booking data from the response
            response_data = response.json()
            if 'data' in response_data:
                return response_data['data']
            return response_data
        elif response.status_code == 404:
            report_error_to_handler(404, "Booking Error", "Booking with ID {booking_id} not found")
            logger.warning(f"Booking with ID {booking_id} not found")
            return None
        else:
            report_error_to_handler({response.status_code}, {response.text}, f"Error retrieving booking: Status {response.status_code}, {response.text}")
            logger.error(f"Error retrieving booking: Status {response.status_code}, {response.text}")
            return None
    except requests.RequestException as e:
        report_error_to_handler(500, "Booking log Connection error", str(e))
        logger.error(f"Error connecting to booking log service: {str(e)}")
        return None

def update_car_availability(car_id, is_available):
    """
    This is to change car availability status
    """
    # Updated URL based on car service API endpoint
    url = f"{CAR_AVAILABILITY_SERVICE_URL}/car/{car_id}/availability"
    payload = {"available": is_available}
    
    try:
        logger.info(f"Updating car {car_id} availability to {is_available}")
        response = requests.put(url, json=payload, timeout=5)
        
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else None,
            "message": "Success" if response.status_code == 200 else response.text
        }
    except requests.RequestException as e:
        report_error_to_handler(500, "Connectivity Error", f"Error connecting to car availability service: {str(e)}")
        logger.error(f"Error calling car availability service: {str(e)}")
        return {
            "status_code": 500,
            "data": None,
            "message": f"Error connecting to car availability service: {str(e)}"
        }

def make_car_available(car_id, booking_id):
    """
    Make a car available again after a booking ends.
    This function is called by the scheduler.
    """
    try:
        logger.info(f"Making car {car_id} available again after booking {booking_id}")
        response = update_car_availability(car_id, True)
        
        if response.get('status_code') != 200:
            status_code = response.get('status_code', 500)  # Default to 500 if missing
            report_error_to_handler(status_code, "Car Availability Failure", f"Failed to make car {car_id} available again: {response.get('message')}") 
            logger.error(f"Failed to make car {car_id} available again: {response.get('message')}")

        else:
            logger.info(f"Successfully made car {car_id} available again after booking {booking_id}")
            
            # Update booking status to 'ended' if booking is still active
            try:
                booking_details = get_booking_details(booking_id)
                if booking_details and booking_details.get('booking_status') == 'in_progress':
                    update_booking_status(booking_id, 'ended')
            except Exception as e:
                error_message = f"Error updating booking status: {str(e)}"
                report_error_to_handler(500, "Booking Status Update Failure", error_message)
                logger.error(error_message)
    except Exception as e:
        error_message = f"Error making car {car_id} available again: {str(e)}"
        report_error_to_handler(500, "Car Availability Failure", error_message)
        logger.error(error_message)


def update_booking_status(booking_id, payment_id=None):

    booking_service_url = f"{BOOKING_LOG_SERVICE_URL}/v1/update-status/{booking_id}"

    update_payload = {
        "booking_status": "in_progress"
    }

    if payment_id:
        update_payload.update({
            "payment_status": "paid",
            "transaction_id": payment_id
        })
    
    try:
        logger.info(f"Updating booking {booking_id} with status='in progress' " + 
                    (f" and payment ID {payment_id}" if payment_id else ""))
        
        booking_update_response = requests.put(booking_service_url, json=update_payload, timeout=5)
        
        if booking_update_response.status_code == 200:
            logger.info(f"Successfully updated booking {booking_id} status to in progress ")
            return True
        else:
            report_error_to_handler({booking_update_response.status_code}, "Booking status update failure", {booking_update_response.text})
            logger.error(f"Failed to update booking status: Status {booking_update_response.status_code}, {booking_update_response.text}")
            return False
    except requests.RequestException as e:
        error_message = f"Error connecting to booking log service: {str(e)}"
        report_error_to_handler(503, "Booking Log Service Unavailable", error_message)
        logger.error(error_message)
        return False

def publish_notification(booking_id):
    """
    gets booking details of the booking_id argument
    publishes a message to the notification queue on rabbitmq broker
    returns tuple of Response JSON object, int error code 
    """
    try:
            booking_details = get_booking_details(booking_id)
            phone_number = booking_details.get("contact_number")
            start_time = booking_details.get("start_time")

            end_time =  booking_details.get("end_time")
            car_id =  booking_details.get("car_id")
            message = "Your booking (ID number " + booking_id + ") is confirmed. Details:\nStart Time: " + start_time + "\nEnd Time: " + end_time + "\nCar ID: " + car_id
            
            success = channel.basic_publish(
                exchange=exchange_name, 
                routing_key="order.notif", 
                body= json.dumps({'phone_number' : phone_number, 'message': message})
            )
            if success:
                return jsonify({'message': 'Notification sent successfully'}), 200
            else:
                report_error_to_handler(500, "Notification failure", 'Failed to send notification')
                return jsonify({'error': 'Failed to send notification'}), 500
    except pika.exceptions.UnroutableError:
        report_error_to_handler(500, "Notification failure", 'Failed to send notification')
        return jsonify({'error': 'Failed to send notification (unroutable)'}), 500
    except Exception as e:
        report_error_to_handler(500, "Internal server error", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@app.route('/<booking_id>/start', methods=['POST'])
def start_booking(booking_id):
    """
    Unified endpoint to process a booking by:
    1. Updating car availability based on time
    2. Processing payment
    3. Updating booking status to 'in_progress'
    """
    try:
#######################
# Get Booking Details #
#######################

        logger.info(f"Processing booking ID: {booking_id}")
        booking_details = get_booking_details(booking_id)
        
        if not booking_details:
            report_error_to_handler(404, "Booking not found", f"Trigger getting booking details MS - No booking found for ID: {booking_id}")
            logger.warning(f"Trigger getting booking details MS - No booking found for ID: {booking_id}")
            return jsonify({"error": "Booking not found"}), 404
        
        current_status = booking_details.get('booking_status')
        if current_status != 'not_started':
            report_error_to_handler(400, "Booking cannot be started", f"Booking {booking_id} is already in progress or completed (status: {current_status})")
            logger.warning(f"Booking {booking_id} is already in progress or completed (status: {current_status})")
            return jsonify({"error": f"Booking cannot be started. Current status: {current_status}"}), 400
        
        car_id = booking_details.get('car_id')
        if not car_id:
            report_error_to_handler(400, "car_id not found", f"No car_id found in booking details for booking ID: {booking_id}")
            logger.error(f"No car_id found in booking details for booking ID: {booking_id}")
            return jsonify({"error": "Booking does not contain car_id"}), 400
        

        start_time = booking_details.get('start_time')
        end_time = booking_details.get('end_time')
        
        if not start_time or not end_time:
            report_error_to_handler(400, "Missing details", f"Booking {booking_id} missing start_time or end_time")
            logger.error(f"Booking {booking_id} missing start_time or end_time")
            return jsonify({"error": "Booking must include start_time and end_time"}), 400
        
        if isinstance(start_time, str):
            try:
                start_time = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try alternative formats
                    start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    report_error_to_handler(400, "Invalid format", f"Invalid start_time format: {start_time}")
                    logger.error(f"Invalid start_time format: {start_time}")
                    return jsonify({"error": "Invalid start_time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
                
        if isinstance(end_time, str):
            try:
                end_time = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try alternative formats
                    end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    report_error_to_handler(400, "Invalid format", f"Invalid end_time format: {end_time}")
                    logger.error(f"Invalid end_time format: {end_time}")
                    return jsonify({"error": "Invalid end_time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
        
        # Get payment details
        total_amount = booking_details['total_amount']
        if not total_amount:
            report_error_to_handler(400, "Missing details", f"No total amount found in booking details for booking ID: {booking_id}")
            logger.error(f"No total amount found in booking details for booking ID: {booking_id}")
            return jsonify({"error": "Booking does not contain total_amount"}), 400
        
    ##############################
    # - Process Payment          # 
    # - Send Notification        #
    # - Update car availability  #
    # - Schedule to end booking  #
    ##############################

        #DOCKER LINK
        payment_service_url = f"{PAYMENT_SERVICE_URL}"
        payment_payload = {
            "booking_id": booking_id,
            "total_amount": total_amount
        }
        logger.info(f"Sending payment request to payment service: {payment_payload}")
        payment_response = requests.post(payment_service_url, json=payment_payload, timeout=5)
        
        if payment_response.status_code != 200:
            error_message = f"Payment service error: {payment_response.status_code}, {payment_response.text}"
            report_error_to_handler(payment_response.status_code, "Payment Processing Failure", error_message)
            logger.error(error_message)
            return jsonify({"error": "Payment processing failed"}), payment_response.status_code

        
        # Process payment response
        payment_result = payment_response.json()
        payment_status = payment_result.get('status')
        
        if payment_status != 'successful':
            report_error_to_handler(500, "Payment processing failed", f"Payment failed for booking ID: {booking_id}")
            logger.error(f"Payment failed for booking ID: {booking_id}")
            return jsonify({"error": "Payment processing failed"}), 500
        # Payment successful, notify customer via SMS
        publish_notification(booking_id)
        
        # publish_notification_response = publish_notification(booking_id)

        # if publish_notification_response[1] != 200:
        #     logger.error(f"Failed to send notification. Error Code: {publish_notification_response[1]}")
        #     return jsonify({"Error": "Failed to send notification"}), publish_notification_response[1]

        # 1: Once payment is successful, update car availability to unavailable
        car_update_response = update_car_availability(car_id, False)
        
        if car_update_response.get('status_code') != 200:
            error_message = f"Failed to update car availability: {car_update_response.get('message')}"
            status_code = car_update_response.get('status_code', 500)

            report_error_to_handler(status_code, "Car Availability Update Failure", error_message)
            logger.error(error_message)

            return jsonify({
                "error": "Failed to update car availability",
                "details": car_update_response.get('message')
            }), status_code

        
        # 2: Schedule car to become available again after booking ends
        logger.info(f"Scheduling car {car_id} to become available at {end_time}")
        scheduler.add_job(
            make_car_available,
            'date',
            run_date=end_time,
            args=[car_id, booking_id],
            id=f"make_available_{booking_id}_{car_id}"
        )
    
        # 3: Update booking with payment details and change status to in_progress
        logger.info(f"Updating booking log - booking_status, payment_status and transaction-id")
        success = update_booking_status(booking_id, payment_result.get('payment_id'))

        if not success:
            report_error_to_handler(500, "Status update failed", "Tigger booking-ms -- Failed to update booking status")
            logger.error("Tigger booking-ms -- Failed to update booking status")
            return jsonify({"warning": "Booking partially processed - status update failed"}), 500

        # Success response
        return jsonify({
            "status": "success",
            "message": "Booking started successfully",
            "details": {
                "booking_id": booking_id,
                "payment_processed": True,
                "car_availability_updated": True,
                "booking_status_updated": True,
                "car_availability_restoration_scheduled": end_time.isoformat(),
                "transaction_id": payment_result.get('payment_id')
            }
        }), 200
    
    except Exception as e:
        report_error_to_handler(500, "Error processing booking", str(e))
        logger.error(f"Error processing booking start: {str(e)}")
        return jsonify({"error": str(e)}), 500
    

 ################
 # Health Check #
 ################

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200   



if __name__ == '__main__':
    import atexit
    connectAMQP()
    testing_mode = True  # Set to True when testing to disable scheduler

    if not testing_mode:
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
    
    app.run(host='0.0.0.0', port=5007, debug=False)