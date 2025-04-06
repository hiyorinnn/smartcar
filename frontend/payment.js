    // Rental Details Side
    
    // Need to get the booking ID from the the previous page
    const booking_id = "booking-1743698647866-qur5uc62t"; // Example booking ID, replace with actual ID from the previous page

    async function getBookingDetails() {
    try {
        const response = await axios.get(`http://127.0.0.1:5006/api/booking/${booking_id}`);
        const data = response.data.data;
        console.log('Booking details:', data);

        const car = data.details.details.car_details;
        const startTime = new Date(data.start_time);
        const endTime = new Date(data.end_time);
        const durationHours = Math.round((endTime - startTime) / (1000 * 60 * 60) * 100) / 100;

        // Format dates more nicely
        const formatDate = (date) => {
        const options = { 
            weekday: 'short',
            month: 'short', 
            day: 'numeric',
            hour: '2-digit', 
            minute: '2-digit'
        };
        return date.toLocaleDateString('en-US', options);
        };

        // Populate HTML with enhanced formatting
        document.getElementById('car-make-model').innerText = `${car.make} ${car.model}`;
        document.getElementById('price-per-hour').innerText = `$${car.price_per_hour}/hr`;
        document.getElementById('start-time').innerText = formatDate(startTime);
        document.getElementById('end-time').innerText = formatDate(endTime);
        document.getElementById('duration').innerText = `${durationHours} hours`;
        document.getElementById('total-price-final').innerText = `$${data.total_amount}`;

    } catch (error) {
        console.error('Error fetching booking:', error);
    }
    }
    document.addEventListener('DOMContentLoaded', getBookingDetails);


    // Payment Side - Using Stripe 
const stripe = Stripe('pk_test_51R7XLM4Jm41usPZB8LXUvo3nFp9ItuWiFCOrksMZWQWqgcyAwRqILKJKReuEeVsHd2yVVY4OdQwecWKfZ4lVbeA000vB8ojdqL');

document.addEventListener('DOMContentLoaded', async () => {
// call payment api 
  const response = await fetch('http://localhost:5008/api/v1/payments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ booking_id: {booking_id} }) 
  });

  const data = await response.json();
  const clientSecret = data.client_secret;

  const elements = stripe.elements({ clientSecret });
  const paymentElement = elements.create("payment");
  paymentElement.mount("#payment-element");


  const form = document.getElementById("payment-form");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: "./success.html",
        cancel_url: "./error.html", 
      },
    });

    if (error) {
      const messageContainer = document.querySelector("#error-message");
      messageContainer.textContent = error.message;
    }
  });
});
