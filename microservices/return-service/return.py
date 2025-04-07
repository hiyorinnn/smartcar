# import sys
# import os
# import pika
# import json
import base64
# import requests
from flask_cors import CORS
from flask import Flask, jsonify, request, redirect

app = Flask(__name__)
CORS(app)

# Declare all the URLs to the microservices
PAYMENTURL = ""  # To ask from Joyce
NOTIFICATIONURL = ""
VIOLATIONLOGURL = "https://personal-qednlunm.outsystemscloud.com/violationlog/rest/violationlog/createViolationLog"
UPLOADURL = "http://aiprocessing:9000/api/upload"
REKOGNITIONURL = "http://aiprocessing:9000/api/rekognition"
BOOKINGLOGURL = "http://booking_log:5006/api/booking/{}"

# RabbitMQ Configuration
# rabbit_host = "localhost"
# rabbit_port = 5672
# exchange_name = "order_topic"
# exchange_type = "topic"
# connection = None 
# channel = None

# def connectAMQP():
#     global connection
#     global channel

#     print("  Connecting to AMQP broker...")
#     try:
#         connection, channel = amqp.connect(
#                 hostname=rabbit_host,
#                 port=rabbit_port,
#                 exchange_name=exchange_name,
#                 exchange_type=exchange_type,
#         )
#     except Exception as exception:
#         print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
#         exit(1) # terminate

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

        # print("reach here")
        # print(booking_id)
        # # Retrieve booking details
        # booking_response = requests.get(BOOKINGLOGURL.format(booking_id))

        # if booking_response.status_code == 404:
        #     return jsonify({'error': 'Booking not found'}), 404
        # elif booking_response.status_code != 200:
        #     return jsonify({'error': 'Error retrieving booking logs'}), 500

        # # Upload images
        # upload_response = requests.post(UPLOADURL, json=payload)

        # print("reached here")

        # if upload_response.status_code != 200:
        #     return jsonify({'error': 'Failed to upload images'}), 500

        # upload_data = upload_response.json()

        # Analyze images with Rekognition
        # rekognition_response = requests.post(REKOGNITIONURL, json=upload_data)

        # if rekognition_response.status_code != 200:
        #     return jsonify({'error': 'Error processing images'}), 500

        # rekognition_data = rekognition_response.json()
        # defect_count = rekognition_data.get('defect_count', 0)

        # uncomment to test the above part
        # return jsonify({"defect_count": 1})

        #uncomment to test log violations
        defect_count = 1

        return jsonify({'error': 'Missing booking ID or total charge in violation response'}), 500

        # # Log violations if there are defects
        # if defect_count > 0:
        #     violation_response = requests.post(VIOLATIONLOGURL, json={'booking_id': booking_id, 'defect_count': defect_count})

        #     if violation_response.status_code != 200:
        #         return jsonify({'error': 'Error logging violations'}), 500

        #     # Ensure violation_response has both 'booking_id' and 'total_charge'
        #     violation_data = violation_response.json()

        #     # Extract 'booking_id' and 'total_charge' from the nested response structure
        #     result_data = violation_data.get("Result", {})
        #     get_all_violation_log = result_data.get("GetAllViolationLog", {})

        #     # Extract the 'booking_id' and 'total_charge'
        #     booking_id = get_all_violation_log.get('booking_id')
        #     total_charge = get_all_violation_log.get('total_charge')

        #     # Check if 'booking_id' and 'total_charge' are available
        #     if booking_id is None or total_charge is None:
        #         return jsonify({'error': 'Missing booking ID or total charge in violation response'}), 500
            
        #     # Return the 'total_charge' in the response
        #     return jsonify({'total_charge': total_charge}), 200

        # Mock up data for malcolm to use
            # total_charge = 100
            # result_data = {{'total_charge': total_charge}}

            # try:
            #     phone_number = booking_response.data.phone_number.value
            #     success = channel.basic_publish(
            #         exchange=exchange_name, 
            #         routing_key="order.notif", 
            #         body= json.dumps({'booking_id': booking_id, 'phone_number' : phone_number, 'message': 'Your vehicle return process is complete.'})
            #     )
            #     if success:
            #         return jsonify({'message': 'Vehicle return process completed successfully'}), 200
            #     else:
            #         return jsonify({'error': 'Failed to send notification'}), 500
            # except pika.exceptions.UnroutableError:
            #     return jsonify({'error': 'Failed to send notification'}), 500
            # except Exception as e:
            #     return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

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
    app.run(debug=True, host='0.0.0.0', port=5011)
