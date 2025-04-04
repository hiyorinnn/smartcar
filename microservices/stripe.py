import os
import stripe
from flask import Flask, jsonify, request, render_template, redirect

app = Flask(__name__,
            static_url_path='',
            static_folder='.')

# Initialize Stripe with your secret key
# This is your test secret API key that you provided
stripe.api_key = 'sk_test_51R7XLM4Jm41usPZBwNr5slG3GHhThtJ4LLHe9MpwsXxnzIT2c11AKYoHGLvO0KwxCEGztfwuI3ozrQ0mAiqJMcM400uwoLUqju'

# The publishable key to be passed to the frontend
stripe_publishable_key = 'pk_test_51R7XLM4Jm41usPZB8LXUvo3nFp9ItuWiFCOrksMZWQWqgcyAwRqILKJKReuEeVsHd2yVVY4OdQwecWKfZ4lVbeA000vB8ojdqL'

@app.route('/')
def index():
    # Fake data - should call from booking service to get details of booking
    car_data = {
        'make_model': 'Tesla Model 3',
        'price_per_hour': 25.99,
        'rental_date': '2025-04-01',
        'duration_hours': 4,
        'total_price': 103.96  # 25.99 * 4
    }
    return render_template('../frontend/checkout.html', 
                           stripe_key=stripe_publishable_key,
                           car_data=car_data)

@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        data = request.json
        
        # If no items are provided, use the default fake data for testing
        if not data or 'items' not in data or not data['items']:
            # Default testing data for car rental
            items = [
                {
                    'id': 'car-rental',
                    'name': 'Tesla Model 3 (4 hours)',
                    'price': 103.96
                }
            ]
        else:
            items = data['items']
        
        # Get order ID or generate one
        order_id = data.get('order_id', f"order_{stripe.util.random_id()}")
        
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=calculate_order_amount(items),  # Amount in cents
            currency='sgd',
            automatic_payment_methods={
                'enabled': True,
            },
            metadata={
                'order_id': order_id,
                'car_model': items[0].get('name', 'Unknown Car'),
                'rental_duration': items[0].get('description', '4 hours')
            }
        )
        
        return jsonify({
            'clientSecret': intent.client_secret
        })
    
    except Exception as e:
        return jsonify(error=str(e)), 403

def calculate_order_amount(items): ## this should be handled by the rental composite service
    """Calculate the total order amount based on the items."""

    # Calculate the total amount based on the items in the cart
    total = sum(item.get('price', 0) for item in items)
    # Convert to cents for Stripe (Stripe requires amounts in cents)
    return int(total * 100)

@app.route('/checkout-success')
def success():
    return render_template('../frontend/checkout-success.html')

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_your_test_webhook_secret_here')

    try:
        # Verify the event came from Stripe
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            handle_successful_payment(payment_intent)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            handle_failed_payment(payment_intent)
        # ... handle other event types as needed
        
        return jsonify(success=True)
        
    except stripe.error.SignatureVerificationError:
        return jsonify(error='Invalid signature'), 400
    except Exception as e:
        return jsonify(error=str(e)), 400

def handle_successful_payment(payment_intent):
    """Update your database, send confirmation emails, etc."""
    print(f"Payment succeeded for intent: {payment_intent['id']}")
    # In a real application, you would:
    # 1. Mark the car as reserved for the specified time
    # 2. Create a reservation record in your database
    # 3. Send a confirmation email to the customer
    # 4. Update inventory systems, etc.
    
def handle_failed_payment(payment_intent):
    """Handle failed payment, notify customer, etc."""
    print(f"Payment failed for intent: {payment_intent['id']}")
    # In a real application, you would:
    # 1. Log the failure
    # 2. Maybe send a failure notification to the customer
    # 3. Keep the car available for other rentals

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(port=4242, debug=True)