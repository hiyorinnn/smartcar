// Rental Details Side



const params = new URLSearchParams(window.location.search);
const booking_id = params.get("bookingId");  // Ensure that the URL has ?bookingId=booking-xxx

async function getBookingDetails() {
  try {
    const response = await axios.get(
      `http://127.0.0.1:5006/api/booking/${booking_id}`
    );
    const data = response.data.data;
    console.log("Booking details:", data);

    // Convert to SG time +8h
    const add8Hours = (utcString) => {
      const date = new Date(utcString);
      // Add 8 hours (8 * 60 * 60 * 1000 milliseconds)
      date.setTime(date.getTime() + 8 * 60 * 60 * 1000);
      return date;
    };

    const car = data.details.details.car_details;
    const startTime = add8Hours(data.start_time);
    const endTime = add8Hours(data.end_time);
    const durationHours =
      Math.round(((endTime - startTime) / (1000 * 60 * 60)) * 100) / 100;

    const formatDate = (date) => {
      const options = {
        weekday: "short",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "Asia/Singapore",
      };
      return date.toLocaleString("en-SG", options);
    };

    // Populate HTML with enhanced formatting
    document.getElementById(
      "car-make-model"
    ).innerText = `${car.make} ${car.model}`;
    document.getElementById(
      "price-per-hour"
    ).innerText = `$${car.price_per_hour}/hr`;
    document.getElementById("start-time").innerText = formatDate(startTime);
    document.getElementById("end-time").innerText = formatDate(endTime);
    document.getElementById("duration").innerText = `${durationHours} hours`;
    document.getElementById(
      "total-price-final"
    ).innerText = `$${data.total_amount}`;
  } catch (error) {
    console.error("Error fetching booking:", error);
  }
}
document.addEventListener("DOMContentLoaded", getBookingDetails);

// Payment Side - Using Stripe
const stripe = Stripe(
  "pk_test_51R7XLM4Jm41usPZB8LXUvo3nFp9ItuWiFCOrksMZWQWqgcyAwRqILKJKReuEeVsHd2yVVY4OdQwecWKfZ4lVbeA000vB8ojdqL"
);

// call payment api
document.addEventListener("DOMContentLoaded", async () => {
  try {
    const response = await axios.post(
      "http://localhost:5008/api/v1/payments",
      {
        booking_id: booking_id, // Ensure booking_id is defined in your scope
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    const data = response.data;
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
          // Change this link accordingly to ur own desktop
          return_url: "http://localhost/GitHub/smartcar/frontend/success.html",
          //cancel_url: "./error.html",
        },
      });

      if (error) {
        const messageContainer = document.querySelector("#error-message");
        messageContainer.textContent = error.message;
      }
    });
  } catch (error) {
    console.error("Payment API error:", error);
    const messageContainer = document.querySelector("#error-message");
    messageContainer.textContent =
      error.response?.data?.message || error.message;
  }
});
