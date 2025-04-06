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
#rental_composite_URL = os.environ.get('rental_composite_URL', 'http://booking-composite:5002/api/v1')
#booking_log_URL = "http://booking_log:5006/api/booking"

#Local URL 
rental_composite_URL = 'http://localhost:5007/api/v1'
booking_log_URL = "http://localhost:5006/api/booking"

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

@app.route('/api/v1/payments/<payment_id>/confirm', methods=['POST'])
def confirm_payment(payment_id):
    """
    Confirm a payment after the client has completed Stripe's payment flow
    
    Expected payload:
    {
        "stripe_payment_intent_id": "string"
    }
    """
    try:
        data = request.json
        stripe_payment_intent_id = data.get('stripe_payment_intent_id')
        
        if not stripe_payment_intent_id:
            return jsonify({"error": "stripe_payment_intent_id is required"}), 400
            
        logger.info(f"Confirming payment intent: {stripe_payment_intent_id} for payment ID: {payment_id}")
        
        # Retrieve the payment intent from Stripe
        intent = stripe.PaymentIntent.retrieve(stripe_payment_intent_id)
        
        if intent.status == 'succeeded':
            # Get the booking ID from the metadata
            booking_id = intent.metadata.get('booking_id')
            
            if booking_id:
                # Update the rental-composite service with payment confirmation
                try:
                    logger.info(f"Notifying rental-composite service about payment for booking ID: {booking_id}")
                    update_response = requests.patch(
                        f"{rental_composite_URL}/bookings/{booking_id}/payment",
                        json={
                            "payment_id": payment_id,
                            "payment_status": "successful",
                            "amount_paid": intent.amount / 100,
                            "currency": intent.currency
                        },
                        timeout=5
                    )
                    
                    if update_response.status_code != 200:
                        logger.warning(f"Failed to update booking-composite: {update_response.status_code}, {update_response.text}")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error notifying rental-composite service: {str(e)}")
            
            return jsonify({
                "status": "successful",
                "payment_id": payment_id,
                "booking_id": booking_id,
                "stripe_status": intent.status,
                "amount": intent.amount / 100,  # Convert to dollars, instead of cents 
                "currency": intent.currency
            }), 200
        else:
            logger.warning(f"Payment intent {stripe_payment_intent_id} has status: {intent.status}")
            return jsonify({
                "status": "pending",
                "payment_id": payment_id,
                "stripe_status": intent.status,
                "message": "Payment has not been completed"
            }), 202
            
    except Exception as e:
        logger.error(f"Error confirming payment: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5008))
    app.run(host='0.0.0.0', port=port)