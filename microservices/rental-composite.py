from flask import Flask, request, jsonify
import requests
import logging
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Create a scheduler for handling timed car availability updates
scheduler = BackgroundScheduler()
# scheduler.start()

#For use with Docker
CAR_AVAILABILITY_SERVICE_URL = "http://car_available:5000"  
BOOKING_LOG_SERVICE_URL = "http://booking_log:5006/api" 

# For local testing
# CAR_AVAILABILITY_SERVICE_URL = "http://localhost:5000"
# BOOKING_LOG_SERVICE_URL = "http://127.0.0.1:5006/api"

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
            logger.warning(f"Booking with ID {booking_id} not found")
            return None
        else:
            logger.error(f"Error retrieving booking: Status {response.status_code}, {response.text}")
            return None
    except requests.RequestException as e:
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
            logger.error(f"Failed to make car {car_id} available again: {response.get('message')}")
        else:
            logger.info(f"Successfully made car {car_id} available again after booking {booking_id}")
            
            # Update booking status to 'ended' if booking is still active
            try:
                booking_details = get_booking_details(booking_id)
                if booking_details and booking_details.get('booking_status') == 'in_progress':
                    update_booking_status(booking_id, 'ended')
            except Exception as e:
                logger.error(f"Error updating booking status: {str(e)}")
    except Exception as e:
        logger.error(f"Error making car {car_id} available again: {str(e)}")

def update_booking_status(booking_id, status):
    """
    Update the status of a booking
    
    Args:
        booking_id: ID of the booking to update
        status: New status ('not_started', 'in_progress', or 'ended')
    
    Returns:
        True if successful, False otherwise
    """
    url = f"{BOOKING_LOG_SERVICE_URL}/booking-logs/{booking_id}/status"
    payload = {"booking_status": status}
    
    try:
        logger.info(f"Updating booking {booking_id} status to {status}")
        response = requests.put(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            logger.info(f"Successfully updated booking {booking_id} status to {status}")
            return True
        else:
            logger.error(f"Failed to update booking status: Status {response.status_code}, {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"Error connecting to booking log service: {str(e)}")
        return False


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
            logger.warning(f"No booking found for ID: {booking_id}")
            return jsonify({"error": "Booking not found"}), 404
        
        current_status = booking_details.get('booking_status')
        if current_status != 'not_started':
            logger.warning(f"Booking {booking_id} is already in progress or completed (status: {current_status})")
            return jsonify({"error": f"Booking cannot be started. Current status: {current_status}"}), 400
        
        car_id = booking_details.get('car_id')
        if not car_id:
            logger.error(f"No car_id found in booking details for booking ID: {booking_id}")
            return jsonify({"error": "Booking does not contain car_id"}), 400
        

        start_time = booking_details.get('start_time')
        end_time = booking_details.get('end_time')
        
        if not start_time or not end_time:
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
                    logger.error(f"Invalid end_time format: {end_time}")
                    return jsonify({"error": "Invalid end_time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
        
        # Get payment details
        total_amount = booking_details['total_amount']
        if not total_amount:
            logger.error(f"No total amount found in booking details for booking ID: {booking_id}")
            return jsonify({"error": "Booking does not contain total_amount"}), 400
        
    ##############################
    # Process Payment            # 
    # - update car availability  #
    # - schedule to end booking  #
    ##############################

        #Local link
        payment_service_url = "http://localhost:5008/api/v1/payments"
        payment_payload = {
            "booking_id": booking_id,
            "total_amount": total_amount
        }
        logger.info(f"Sending payment request to payment service: {payment_payload}")
        payment_response = requests.post(payment_service_url, json=payment_payload, timeout=5)
        
        if payment_response.status_code != 200:
            logger.error(f"Payment service error: {payment_response.status_code}, {payment_response.text}")
            return jsonify({"error": "Payment processing failed"}), payment_response.status_code
        
        # Process payment response
        payment_result = payment_response.json()
        payment_status = payment_result.get('status')
        
        if payment_status != 'successful':
            logger.error(f"Payment failed for booking ID: {booking_id}")
            return jsonify({"error": "Payment processing failed"}), 500
        
        # 1: Once payment is successful, update car availability to unavailable
        car_update_response = update_car_availability(car_id, False)
        
        if car_update_response.get('status_code') != 200:
            logger.error(f"Failed to update car availability: {car_update_response.get('message')}")
            return jsonify({
                "error": "Failed to update car availability",
                "details": car_update_response.get('message')
            }), car_update_response.get('status_code', 500)
        
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
        booking_service_url = f"http://localhost:5006/api/v1/update-status/{booking_id}"
        update_payload = {
            "payment_status": "paid",
            "transaction_id": payment_result.get('payment_id'),
            "booking_status": "in_progress"
        }
        logger.info(f"Updating booking with payment status and changing status to in_progress: {update_payload}")
        
        booking_update_response = requests.put(booking_service_url, json=update_payload, timeout=5)
        
        if booking_update_response.status_code != 200:
            logger.error(f"Failed to update booking: {booking_update_response.status_code}, {booking_update_response.text}")
            # Even if this fails, we've already processed payment and updated car availability
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
        logger.error(f"Error processing booking start: {str(e)}")
        return jsonify({"error": str(e)}), 500
    

 ################
 # Health Check #
 # ##############

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200   



if __name__ == '__main__':
    import atexit
    testing_mode = False  # Set to True when testing to disable scheduler

    if not testing_mode:
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
    
    app.run(host='0.0.0.0', port=5007, debug=False)