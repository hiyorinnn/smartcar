import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Declare all the constants 
BOOKINGLOGURL = "http://localhost:5004/api/booking-log/"

@app.route('/api/fetch', methods=['POST'])
def fetch_data():
    
    # Get the user_id from the request body
    user_id = request.args.get("userid")
    
    if not user_id:
        return jsonify({"code": 400, "message": "User ID is required"}), 400
    
    # Construct the URL for the /api/booking-log/<user_id> endpoint using the declared constant
    booking_log_url = f"{BOOKINGLOGURL}{user_id}"

    try:
        # Call the /api/booking-log/<user_id> microservice internally
        response = requests.get(booking_log_url)

        if response.status_code != 200:
            return jsonify({"code": response.status_code, "message": "Error retrieving booking logs"}), 500

        # Process the response (booking logs) and send back the combined result
        booking_logs = response.json().get('data', [])

        # You can add more service calls here if needed, such as calling other microservices
        # Then return the combined results back to the user
        return jsonify({
            "status": "success",
            "message": "Data fetched successfully",
            "booking_logs": booking_logs
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"code": 500, "message": "Error while calling the booking log service", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5004)
