<template>
  <div class="container">
    <h1 class="title">Booking Page</h1>
    <div class="card">
      <div class="card-body">
        <p>Select a car and proceed with booking.</p>
        <button class="btn btn-primary">Proceed to Payment</button>
      </div>
    </div>
  </div>
</template>

<script>
// Import logError from utils.js
import { logError } from "@/utils";

export default {
  name: 'BookingPage',
  methods: {
    proceedToPayment() {
      try {
        // Simulate a possible error in this method (e.g., failed booking process)
        throw new Error("Payment gateway not responding.");
      } catch (error) {
        // Log the error to the Flask microservice
        logError("Booking Error", error.message);
      }
    }
  }
};
</script>

<style scoped>
.container {
  max-width: 600px;
  margin: 50px auto;
  text-align: center;
}

.title {
  font-size: 2rem;
  color: #2c3e50;
}

.card {
  border-radius: 12px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.btn-primary {
  background-color: #007bff;
  border: none;
  padding: 10px 15px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
}

.btn-primary:hover {
  background-color: #0056b3;
}
</style>
