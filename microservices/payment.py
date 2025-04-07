from flask import Flask, request, jsonify
from flask_cors import CORS
import stripe
import os
import logging
import uuid
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


# Configure Stripe API key
stripe.api_key = os.environ.get('STRIPE_API_KEY', 'sk_test_51R7XLM4Jm41usPZBwNr5slG3GHhThtJ4LLHe9MpwsXxnzIT2c11AKYoHGLvO0KwxCEGztfwuI3ozrQ0mAiqJMcM400uwoLUqju')

# rental-composite service configuration

#Docker URL
rental_composite_URL = os.environ.get('rental_composite_URL', 'http://rental-composite:5007/api/v1')
booking_log_URL = "http://booking_log:5006/api/booking"

# #Local URL 
# rental_composite_URL = 'http://localhost:5007/api/v1'
# booking_log_URL = "http://localhost:5006/api/booking"

@app.route('/api/v1/payments', methods=['POST'])
def process_payment():
    try:
        data = request.json
        logger.info(f"Received payment request: {data}")
        
        # Validate required fields
        booking_id = data.get('booking_id')
        
        if not booking_id:
            logger.error("Missing booking_id in request")
            return jsonify({"error": "booking_id is required"}), 400
        
        logger.info(f"Fetching booking details for booking ID: {booking_id}")
        try:
            booking_response = requests.get(f"{booking_log_URL}/{booking_id}", timeout=5)
            
            if booking_response.status_code != 200:
                logger.error(f"Failed to get booking details: {booking_response.status_code}, {booking_response.text}")
                return jsonify({"error": "Failed to get booking details from rental-composite service"}), 500
                
            booking_details = booking_response.json()
            
            total_amount = booking_details['data']['total_amount']
            
            if not total_amount:
                logger.error(f"No total_amount found in booking details for booking ID: {booking_id}")
                return jsonify({"error": "booking does not contain total_amount"}), 400
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with rental-composite service: {str(e)}")
            return jsonify({"error": "Failed to communicate with rental-composite service"}), 500

        # Create a payment intent with Stripe
        # Amount needs to be in cents for Stripe
        amount_in_cents = int(float(total_amount) * 100)
        
        payment_intent_data = {
            "amount": amount_in_cents,
            "currency": "sgd",
            "metadata": {
                "booking_id": booking_id
            }
        }
                    
        logger.info(f"Creating Stripe payment intent for {amount_in_cents} cents ({total_amount} $SGD)")
        
        # Create the payment intent
        intent = stripe.PaymentIntent.create(**payment_intent_data)
        
        # Generate a unique payment ID for our system
        payment_id = str(uuid.uuid4())
        
        # Return client secret and payment details
        return jsonify({
            "status": "successful",
            "payment_id": payment_id,
            "stripe_payment_intent_id": intent.id,
            "client_secret": intent.client_secret,
            "amount": total_amount,
            "currency": 'sgd',
            "created_at": datetime.now().isoformat()
        }), 200
            
    except stripe.error.StripeError as e:
        # Handle Stripe-specific errors
        logger.error(f"Stripe error: {str(e)}")
        return jsonify({
            "status": "failed",
            "error": str(e)
        }), 400
        
    except Exception as e:
        # Handle general errors
        logger.error(f"Error processing payment: {str(e)}")
        return jsonify({
            "status": "failed",
            "error": str(e)
        }), 500

import sys
@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_3e285bea74983dec8c4fb3eac977f18e248e35a7d28401298d07b7178d1d719b')

    if not sig_header:
        print("❌ Missing Stripe-Signature header", file=sys.stderr)
        return jsonify({"error": "Missing signature"}), 400

    try:
        print(f"📦 Raw Payload: {payload}", file=sys.stderr)
        print(f"📨 Stripe-Signature: {sig_header}", file=sys.stderr)

        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=endpoint_secret
        )

    except ValueError as e:
        print(f"❌ Invalid payload: {e}", file=sys.stderr)
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        print(f"❌ Invalid signature: {e}", file=sys.stderr)
        return jsonify({"error": "Invalid signature"}), 400

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        booking_id = intent['metadata'].get('booking_id')

        payment_id = str(uuid.uuid4())
        amount = intent['amount'] / 100
        currency = intent['currency']

        if booking_id:
            try:
                logger.info(f"Webhook: Notifying rental-composite about payment for booking {booking_id}")
                response = requests.patch(
                    f"{rental_composite_URL}/bookings/{booking_id}/payment",
                    json={
                        "transaction": payment_id,
                        "payment_status": "paid",
                        "amount_paid": amount,
                        "currency": currency
                    },
                    timeout=5
                )
                if response.status_code != 200:
                    logger.warning(f"Webhook: Failed to update booking-composite: {response.status_code}, {response.text}")
                
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Webhook: Error notifying rental-composite: {str(e)}")
                

    return jsonify({"status": "received"}), 200



@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5008))
    app.run(host='0.0.0.0', port=port)