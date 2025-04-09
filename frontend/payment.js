// Rental Details Side

const bookingData = JSON.parse(localStorage.getItem("bookingData"));

if (!bookingData || !bookingData.booking_id) {
  alert("No booking data found. Please book a car first.");
  window.location.href = "./booking.html";
}

const booking_id = bookingData.booking_id;
async function getBookingDetails() {
  try {
    const response = await axios.get(
      `http://127.0.0.1:5006/api/booking/${booking_id}`
    );
    const data = response.data.data;
    console.log("Booking details:", data);

    // Convert to SG time +8h
    // edit 9/4/25 Uh I don't think this is needed now, so I'm changing it.
    const convertToDateString = (utcString) => {
      const date = new Date(utcString);
      date.setTime(date.getTime() + 0 * 60 * 60 * 1000);
      return date;
    };

    const car = data.details.details.car_details;
    const startTime = convertToDateString(data.start_time);
    const endTime = convertToDateString(data.end_time);
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
        booking_id: booking_id, 
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

      // Show loading state
      const submitButton = document.getElementById("submit");
      submitButton.disabled = true;
      submitButton.innerHTML = `<div class="spinner"></div> Processing payment...`;

      try {
        const { error, paymentIntent } = await stripe.confirmPayment({
          elements,
          redirect: "if_required",
          confirmParams: {
            return_url: window.location.href,
          },
        });

        if (error) {
          // Handle payment errors
          const messageContainer = document.querySelector("#error-message");
          messageContainer.textContent = error.message;
          submitButton.disabled = false;
          submitButton.innerHTML = "Pay";
          return;
        }
        
        if (paymentIntent && paymentIntent.status === "succeeded") {
          console.log("Payment successful, starting booking process...");
          
          // Call the rental-composite service to start the booking
          try {
            const rentalResponse = await axios.post(
              `http://localhost:5007/${booking_id}/start`
            );
            
            console.log("Booking started successfully:", rentalResponse.data);
            
            // After successful booking start, redirect to success page
            // window.location.href = "http://localhost/GitHub/smartcar/frontend/success.html";
            window.location.href = "./success.html"
          } catch (rentalError) {
            console.error("Error starting booking:", rentalError);
            const messageContainer = document.querySelector("#error-message");
            messageContainer.textContent = 
              "Payment successful, but we couldn't start your booking. Please contact support.";
            submitButton.disabled = false;
            submitButton.innerHTML = "Try Again";
          }
        }
      } catch (submitError) {
        console.error("Error during payment submission:", submitError);
        const messageContainer = document.querySelector("#error-message");
        messageContainer.textContent = "An unexpected error occurred. Please try again.";
        submitButton.disabled = false;
        submitButton.innerHTML = "Pay";
      }
    });
  } catch (error) {
    console.error("Payment API error:", error);
    const messageContainer = document.querySelector("#error-message");
    messageContainer.textContent =
      error.response?.data?.message || error.message;
  }
});