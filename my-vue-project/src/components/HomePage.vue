<!-- HomePage.vue -->
<template>
  <div class="home-container">
    <h1>{{ msg }}</h1>
    <p>Find and rent the best car near you!</p>
    <button class="btn btn-success">Search Cars</button>
  </div>
</template>

<script>
// Import logError from utils.js
import { logError } from "@/utils";

export default {
  name: 'HomePage',
  props: {
    msg: String
  },
  methods: {
    searchCars() {
      try {
        // Simulate a possible error in this method (e.g., API call failure)
        throw new Error("Unable to fetch cars near you.");
      } catch (error) {
        // Log the error to the Flask microservice
        logError("Search Cars Error", error.message);
      }
    }
  }
};
</script>

<style scoped>
.home-container {
  text-align: center;
  margin-top: 50px;
}

h1 {
  color: #2c3e50;
  font-size: 2.5rem;
}

p {
  font-size: 1.2rem;
  color: #555;
}

.btn-success {
  background-color: #28a745;
  border: none;
  padding: 10px 15px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
}

.btn-success:hover {
  background-color: #218838;
}
</style>
