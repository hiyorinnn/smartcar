from flask import Flask, jsonify, request, redirect
import base64
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Declare all the URLs to the microservices
PAYMENTURL = "To be updated, port: 5000"  # To ask from Joyce
NOTIFICATIONURL = "http://notification:5001/api/send-sms"
VIOLATIONLOGURL = "https://personal-qednlunm.outsystemscloud.com/violationlog/rest/violationlog/createViolationLog"
UPLOADURL = "http://aiprocessing:5003/api/upload"
REKOGNITIONURL = "http://aiprocessing:5003/api/rekognition"
BOOKINGLOGURL = "http://booking:5004/api/booking-log/{booking_id}" #changed from 4-6

@app.route('/api/return-vehicle', methods=['POST'])
def return_vehicle():
    try:
        # Receive data in multipart/form-data format from the frontend
        booking_id = request.form.get('booking_id')
        files = request.files.getlist('images')

        if not booking_id or not files:
            return jsonify({'error': 'Missing booking_id or images'}), 400

        # Prepare images data
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


        # Retrieve booking details
        # booking_response = requests.get(BOOKINGLOGURL.format(booking_id))

        # if booking_response.status_code == 404:
        #     return jsonify({'error': 'Booking not found'}), 404
        # elif booking_response.status_code != 200:
        #     return jsonify({'error': 'Error retrieving booking logs'}), 500

        # Upload images
        upload_response = requests.post(UPLOADURL, json=payload)

        if upload_response.status_code != 200:
            return jsonify({'error': 'Failed to upload images'}), 500

        upload_data = upload_response.json()

        # Analyze images with Rekognition
        rekognition_response = requests.post(REKOGNITIONURL, json=upload_data)

        if rekognition_response.status_code != 200:
            return jsonify({'error': 'Error processing images'}), 500

        rekognition_data = rekognition_response.json()
        defect_count = rekognition_data.get('defect_count', 0)

        return jsonify({"defect_count": defect_count}), 200

        # # Log violations if there are defects
        # if defect_count > 0:
        #     violation_response = requests.post(VIOLATIONLOGURL, json={'booking_id': booking_id, 'defect_count': defect_count})

        #     if violation_response.status_code != 200:
        #         return jsonify({'error': 'Error logging violations'}), 500

        #     # Ensure violation_response has both 'booking_id' and 'total_charge'
        #     violation_data = violation_response.json()
        #     booking_id = violation_data.get('booking_id')
        #     total_charge = violation_data.get('total_charge')

        #     if not booking_id or total_charge is None:
        #         return jsonify({'error': 'Missing booking ID or total charge in violation response'}), 500

        #     # Send notification if defects are found
        #     notification_response = requests.post(NOTIFICATIONURL, json={'booking_id': booking_id, "total_charge": total_charge, 'message': 'You have an outstanding payment.'})

        #     if notification_response.status_code != 200:
        #         return jsonify({'error': 'Failed to send notification'}), 500

        #     # Construct the redirect URL with booking_id and total_charge as query parameters
        #     if notification_response.status_code == 200:
        #         query_string = f"booking_id={booking_id}&total_charge={total_charge}"
        #         payment_url_with_data = f"{PAYMENTURL}?{query_string}"
        #         return redirect(payment_url_with_data)

        # return jsonify({'message': 'Vehicle return process completed successfully'}), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5006)
