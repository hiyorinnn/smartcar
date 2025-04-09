from flask import Flask, request, jsonify
import boto3
import json
import sys
import os
import amqp_lib as amqp


app = Flask(__name__)

#RabbitMQ configuration, consumes all messages with *.notif
rabbit_host = "host.docker.internal"
rabbit_port = 5672
exchange_name = "smartcar_topic"
exchange_type = "topic"
queue_name = "Notification"

# Load AWS credentials from config file
with open("config.json") as config_file:
    config = json.load(config_file)

# Initialize AWS SNS client
sns_client = boto3.client(
    "sns",
    region_name=config.get("AWS_REGION", "ap-southeast-1"),
    aws_access_key_id=config.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=config.get("AWS_SECRET_ACCESS_KEY")
)

#This is the Amazon Resource Number of the SNS Topic Exchange
SNS_TOPIC_ARN = config.get("SNS_TOPIC_ARN")


@app.route("/send-sms", methods=["POST"])
def send_sms(phone_number, message):
    
    if not phone_number or not message:
        return jsonify({"error": "Phone number and message are required"}), 400
    
    try:
        # Subscribe the phone number to the SNS topic
        subscription = sns_client.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol="sms",
            Endpoint=phone_number
        )
        subscription_arn = subscription.get("SubscriptionArn")
        
        # Publish the message to the SNS topic, which the endpoint phone no. will receive
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message
        )
        
        # Unsubscribe the phone number immediately after sending the message
        # This is so that that phone no. will not receive subsequent messages from the topic. 
        # i.e., the notification topic will only have 1 phone no. endpoint receiving a notification at any time.
        if subscription_arn:
            sns_client.unsubscribe(SubscriptionArn=subscription_arn)
        
        return jsonify({"message_id": response["MessageId"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def callback(ch, method, properties, body):
    """
    Callback function to process messages from RabbitMQ.
    
    Args:
    - ch: RabbitMQ channel
    - method: Delivery method
    - properties: 
    - body: Message body (expected to be JSON)
    """
    try:
        # Decode and parse the JSON message
        data = json.loads(body.decode('utf-8'))
        phone_number_raw = data.get("phone_number")
        message = data.get("message")

        if phone_number_raw[0] != "+":
            phone_number = "+65" + phone_number_raw
            
        if not phone_number or not message:
            print("Invalid message format. Missing phone_number or message.")
            return

        # Ensure Flask app context is active
        with app.app_context():
            response = send_sms(phone_number, message)
                
        if response[1] == 200:
            print(f"SMS sent successfully: {response}")
        else:
            print(f"Error: {response}")
        
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError:
        print("Failed to decode JSON message.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        print(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

if __name__ == "__main__":
    print(f"This is {os.path.basename(__file__)} - amqp consumer...")
    try:
        amqp.start_consuming(
            rabbit_host, rabbit_port, exchange_name, exchange_type, queue_name, callback
        )
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
