<template>
  <div class="container">
    <h1 class="title">Location Page</h1>
    <div class="card">
      <div class="card-body">
        <p>Select your location to view available cars.</p>
        <button class="btn btn-info">Find Nearest Cars</button>
      </div>
    </div>
  </div>
</template>

<script>
// Import logError from utils.js
import { logError } from "@/utils";

export default {
  name: 'LocationPage',
  methods: {
    findNearestCars() {
      try {
        // Simulate a possible error in this method (e.g., location fetch failure)
        throw new Error("Location service unavailable.");
      } catch (error) {
        // Log the error to the Flask microservice
        logError("Location Service Error", error.message);
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

.btn-info {
  background-color: #17a2b8;
  border: none;
  padding: 10px 15px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
}

.btn-info:hover {
  background-color: #138496;
}
</style>
