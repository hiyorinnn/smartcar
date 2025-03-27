# All the dependencies
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Declare all the URLs to the microservices
PAYMENTURL = "To be updated, port: 5000" #To ask from Joyce
NOTIFICATIONURL = "http://localhost:5001/api/send-sms" #To ask Malcolm to change the port and the route to standardise
VIOLATIONLOGURL = "To be updated, port: 5002" #To ask from Yun Wen/Malcolm
GENERATEPRESIGNEDURL = "http://localhost:5003/api/generate-presigned-url"
REKOGNITIONURL = "http://localhost:5003/api/rekognition"
BOOKINGLOGURL = "http://localhost:5004/api/booking-log/{booking_id}"
ERRORHANDLINGURL = "http://localhost:5005/api/error-handling/" #To ask Jing Kai to change the port and the route to standardise


@app.route('/api/return-vehicle', methods=['POST'])

# 1. Receive data in JSON format from the car return form frontend page (an example)
    # {
    #   booking_id : 1234,
    #   images: {
    #           image1: {
    #                       file_name: car, 
    #                       file_type: png
    #                    }
    #           image2: {
    #                       file_name: car, 
    #                       file_type: png
    #                    }
    # }

# 2. Retrieve data from the booking-log database using booking_id (Changes made: No more userID)
# If: || code: 200, record found || code: 404, record not found
# If it returns 404, terminate and invoke ERRORHANDLINGURL microservice
# If it returns 200, invoke GENERATEPRESIGNEDURL using the above JSON format
# After receiving the generated pre-signed url for each images in a list (GENERATEPRESIGNEDURL will return something like:
# {
#     "bookingID": "12345",
#     "presigned_urls": [
#         {
#             "image_key": "image1",
#             "presigned_url": "https://s3.amazonaws.com/your-bucket/12345/car_image1.png?AWSAccessKeyId=ACCESS_KEY&Signature=SIGNED_URL&Expires=3600",
#             "bucket": "your-bucket",
#             "file_name": "car_image1.png",
#             "file_type": "image/png"
#         },
#         {
#             "image_key": "image2",
#             "presigned_url": "https://s3.amazonaws.com/your-bucket/12345/car_image2.png?AWSAccessKeyId=ACCESS_KEY&Signature=SIGNED_URL&Expires=3600",
#             "bucket": "your-bucket",
#             "file_name": "car_image2.png",
#             "file_type": "image/png"
#         }
#     ]
# }
# 
# ), then from the response, invoke the REKOGNITIONURL together with the json
# REKOGNITIONURL will return the number of defect_count, 200.
# If received 404, invoke ERRORHANDLINGURL microservice.

# 3. If received 200, invoke VIOLATIONLOGURL.
# VIOLATIONLOGURL will either returns 200 or 404.
# If 404, invoke ERRORHANDLINGURL microservice.

# 4. If 200, invoke NOTIFICATIONURL microservice.
# SMS will be sent to the customers

# Payment scenario abit weird. To be implemented later. Because IDK where payment is invoke from? Link in the SMS to pay? 

@app.route('/api/return-vehicle', methods=['POST'])
def return_vehicle():
    try:
        # 1. Receive data in JSON format from the car return form frontend page
        data = request.get_json()
        booking_id = data.get('booking_id')
        images = data.get('images')

        if not booking_id or not images:
            return jsonify({'error': 'Missing booking_id or images'}), 400

        # 2. Retrieve data from the booking-log database using booking_id
        response = requests.get(BOOKINGLOGURL.format(booking_id))
        
        if response.status_code == 404:
            requests.post(ERRORHANDLINGURL, json={'booking_id': booking_id, 'error': 'Booking not found'})
            return jsonify({'error': 'Booking not found'}), 404
        elif response.status_code != 200:
            return jsonify({'error': 'Error retrieving booking logs'}), 500

        # 3. Invoke GENERATEPRESIGNEDURL to get pre-signed URLs
        presigned_response = requests.post(GENERATEPRESIGNEDURL, json={'bookingID': booking_id, 'images': images})
        
        if presigned_response.status_code != 200:
            return jsonify({'error': 'Failed to generate pre-signed URLs'}), 500

        presigned_data = presigned_response.json()
        
        # 4. Invoke REKOGNITIONURL to analyze the images
        rekognition_response = requests.post(REKOGNITIONURL, json=presigned_data)
        
        if rekognition_response.status_code == 404:
            requests.post(ERRORHANDLINGURL, json={'booking_id': booking_id, 'error': 'Rekognition service failed'})
            return jsonify({'error': 'Rekognition service failed'}), 404
        elif rekognition_response.status_code != 200:
            return jsonify({'error': 'Error processing images'}), 500

        rekognition_data = rekognition_response.json()
        defect_count = rekognition_data.get('defect_count', 0)

        # 5. Invoke VIOLATIONLOGURL if necessary
        violation_response = requests.post(VIOLATIONLOGURL, json={'booking_id': booking_id, 'defect_count': defect_count})
        
        if violation_response.status_code == 404:
            requests.post(ERRORHANDLINGURL, json={'booking_id': booking_id, 'error': 'Violation log service failed'})
            return jsonify({'error': 'Violation log service failed'}), 404
        elif violation_response.status_code != 200:
            return jsonify({'error': 'Error logging violations'}), 500

        # 6. Invoke NOTIFICATIONURL to send an SMS notification
        notification_response = requests.post(NOTIFICATIONURL, json={'booking_id': booking_id, 'message': 'Your vehicle return process is complete.'})
        
        if notification_response.status_code != 200:
            return jsonify({'error': 'Failed to send notification'}), 500

        return jsonify({'message': 'Vehicle return process completed successfully'}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Microservice request failed', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5006)

