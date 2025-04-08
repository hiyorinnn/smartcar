#Composite Microservice for Process 3 of returning the vehicle

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import pika
import sys, os

import rabbitmq.amqp_lib as amqp

app = Flask(__name__)
CORS(app)

#Microservices that connect to this microservice via HTTP requests
payment_URL = "http://localhost:5001/payment"
location_service_URL = "http://localhost:5002/location_service"

# RabbitMQ
rabbit_host = "localhost"
rabbit_port = 5672
exchange_name = "order_topic"
exchange_type = "topic"

connection = None 
channel = None


#to connect to rabbitmq container
def connectAMQP():
    # Use global variables to reduce number of reconnection to RabbitMQ
    # There are better ways but this suffices for our lab
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
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
        exit(1) # terminate

# WIP, this should publish a message to the order_topic exchange, 
# where under the *.notif queue, the notification.py should consume all messages with *.notif, 
# which will then send the SMS to the number, but I can't get it to work coz of some payload error
def processPlaceOrder(result):
    if connection is None or not amqp.is_connection_open(connection):
        connectAMQP()

    message = result

    print("  Publish message with routing_key=order.notif\n")
    channel.basic_publish(
        exchange=exchange_name, 
        routing_key="order.notif", 
        body=message,
    )

result = '{"phone_number" : "+6590967606", "message" : "WAITWTFHOLDON"}'

processPlaceOrder(result)

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for placing an order...")
    connectAMQP()
    app.run(host="0.0.0.0", port=5100, debug=True)
