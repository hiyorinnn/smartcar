import { createRouter, createWebHistory } from 'vue-router';  // Correct import for Vue Router 4
import HomePage from '../components/HomePage.vue';
import LocationPage from '../components/LocationPage.vue';
import BookingPage from '../components/BookingPage.vue';
import PaymentPage from '../components/PaymentPage.vue';

// Define your routes
const routes = [
  {
    path: '/',
    name: 'HomePage',
    component: HomePage,
  },
  {
    path: '/locations',
    name: 'LocationsPage',
    component: LocationPage,
  },
  {
    path: '/booking',
    name: 'BookingPage',
    component: BookingPage,
  },
  {
    path: '/payment',
    name: 'PaymentPage',
    component: PaymentPage,
  },
];

// Create a router instance using the new API
const router = createRouter({
  history: createWebHistory(),  // Use createWebHistory for modern SPA history mode
  routes,  // Define the routes
});

export default router;
