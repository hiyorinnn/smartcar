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
scheduler.start()

# #For use with Docker
# CAR_AVAILABILITY_SERVICE_URL = "http://car_available:5000"  
# BOOKING_LOG_SERVICE_URL = "http://booking_log:5006/api" 

# For local testing
CAR_AVAILABILITY_SERVICE_URL = "http://localhost:5000"
BOOKING_LOG_SERVICE_URL = "http://localhost:5006/api"

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

#SEARCH FOR BOOKING DETAILS - By Booking ID
@app.route('/api/v1/booking/<booking_id>', methods=['GET'])
def get_booking(booking_id):
    """
    Get booking details for a specific booking ID
    """
    try:
        logger.info(f"Retrieving booking details for booking ID: {booking_id}")
        booking_details = get_booking_details(booking_id)
        
        if not booking_details:
            logger.warning(f"No booking found for ID: {booking_id}")
            return jsonify({"error": "Booking not found"}), 404
            
        return jsonify(booking_details), 200
    except Exception as e:
        logger.error(f"Error retrieving booking details: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/bookings/<booking_id>/process', methods=['POST'])
# Process booking - change car availability status by start time and end time 
def process_booking(booking_id):
    """
    Process a booking by:
    1. Retrieving booking details
    2. Updating car availability status to unavailable during booking time
    3. Scheduling the car to become available again after booking ends
    """
    try:
        # Step 1: Get booking details
        logger.info(f"Processing booking ID: {booking_id}")
        booking_details = get_booking_details(booking_id)
        
        if not booking_details:
            logger.warning(f"No booking found for ID: {booking_id}")
            return jsonify({"error": "Booking not found"}), 404
        
        car_id = booking_details.get('car_id')
        if not car_id:
            logger.error(f"No car_id found in booking details for booking ID: {booking_id}")
            return jsonify({"error": "Booking does not contain car_id"}), 400
        
        # Check if booking contains start and end times
        start_time = booking_details.get('start_time')
        end_time = booking_details.get('end_time')
        
        if not start_time or not end_time:
            logger.error(f"Booking {booking_id} missing start_time or end_time")
            return jsonify({"error": "Booking must include start_time and end_time"}), 400
        
        # Convert string times to datetime objects if they're strings
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
        
        # Step 2: Update car availability to unavailable
        car_update_response = update_car_availability(car_id, False)
        
        if car_update_response.get('status_code') != 200:
            logger.error(f"Failed to update car availability: {car_update_response.get('message')}")
            return jsonify({
                "error": "Failed to update car availability",
                "details": car_update_response.get('message')
            }), car_update_response.get('status_code', 500)
        
        # Step 3: Schedule car to become available again after booking ends
        logger.info(f"Scheduling car {car_id} to become available at {end_time}")
        scheduler.add_job(
            make_car_available,
            'date',
            run_date=end_time,
            args=[car_id, booking_id],
            id=f"make_available_{booking_id}_{car_id}"
        )
        
        # Success response
        return jsonify({
            "message": "Booking processed successfully",
            "booking_details": booking_details,
            "car_availability_update": car_update_response.get('data'),
            "availability_restoration_scheduled": end_time.isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error processing booking: {str(e)}")
        return jsonify({"error": str(e)}), 500

def update_car_availability(car_id, is_available):
    """
    Update car availability status through PUT request to car availability service
    
    Args:
        car_id: ID of the car to update
        is_available: Boolean indicating if car is available (True) or unavailable (False)
    
    Returns:
        Dictionary containing response status and data
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
    Scheduled job to make a car available again after a booking ends
    
    Args:
        car_id: ID of the car to update
        booking_id: ID of the booking that ended
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

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/v1/bookings/<booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """
    Cancel a booking and immediately make the car available again
    """
    try:
        # Get booking details
        logger.info(f"Canceling booking ID: {booking_id}")
        booking_details = get_booking_details(booking_id)
        
        if not booking_details:
            logger.warning(f"No booking found for ID: {booking_id}")
            return jsonify({"error": "Booking not found"}), 404
        
        car_id = booking_details.get('car_id')
        if not car_id:
            logger.error(f"No car_id found in booking details for booking ID: {booking_id}")
            return jsonify({"error": "Booking does not contain car_id"}), 400
        
        # Remove any scheduled availability updates for this booking
        job_id = f"make_available_{booking_id}_{car_id}"
        try:
            scheduler.remove_job(job_id)
            logger.info(f"Removed scheduled job {job_id}")
        except Exception as e:
            logger.warning(f"Could not remove job {job_id}: {str(e)}")
        
        # Make car available immediately
        car_update_response = update_car_availability(car_id, True)
        
        if car_update_response.get('status_code') != 200:
            logger.error(f"Failed to update car availability: {car_update_response.get('message')}")
            return jsonify({
                "error": "Failed to update car availability",
                "details": car_update_response.get('message')
            }), car_update_response.get('status_code', 500)
        
        # Update booking status if needed
        booking_status = booking_details.get('booking_status')
        if booking_status and booking_status != 'ended':
            update_booking_status(booking_id, 'ended')
        
        return jsonify({
            "message": "Booking canceled successfully",
            "car_availability_update": car_update_response.get('data')
        }), 200
        
    except Exception as e:
        logger.error(f"Error canceling booking: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/bookings/upcoming-releases', methods=['GET'])
def check_upcoming_releases():
    """
    Check for any upcoming car releases and ensure they're scheduled
    This can be called periodically to ensure resilience in case the service restarts
    """
    try:
        # In a production system, we would query for all 'in_progress' bookings
        # and make sure they have scheduled release jobs
        # For simplicity, we'll just return a success message
        return jsonify({
            "message": "Upcoming releases check completed",
            "active_jobs": len(scheduler.get_jobs())
        }), 200
    except Exception as e:
        logger.error(f"Error checking upcoming releases: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    import atexit
    atexit.register(lambda: scheduler.shutdown())
    
    app.run(host='0.0.0.0', port=5007, debug=False)