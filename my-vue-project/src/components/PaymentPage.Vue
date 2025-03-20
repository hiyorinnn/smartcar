<template>
  <div class="container">
    <h1 class="title">Payment Page</h1>
    <div class="card">
      <div class="card-body">
        <p>Proceed with payment to confirm your booking.</p>
        <button class="btn btn-warning">Pay Now</button>
      </div>
    </div>
  </div>
</template>

<script>
// Import logError from utils.js
import { logError } from "@/utils";

export default {
  name: 'PaymentPage',
  methods: {
    payNow() {
      try {
        // Simulate a possible error in this method (e.g., payment failure)
        throw new Error("Payment processing failed.");
      } catch (error) {
        // Log the error to the Flask microservice
        logError("Payment Error", error.message);
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

.btn-warning {
  background-color: #ffc107;
  border: none;
  padding: 10px 15px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
}

.btn-warning:hover {
  background-color: #e0a800;
}
</style>

  