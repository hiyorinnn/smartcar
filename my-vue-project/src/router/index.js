// Vue 3 requires using createRouter and createWebHistory instead of Vue.use(Router).
import { createRouter, createWebHistory } from 'vue-router';   

// Import the components/pages from the correct path
import HomePage from '../components/HomePage.vue';
import LocationPage from '../components/LocationPage.vue';
import BookingPage from '../components/BookingPage.vue';
import PaymentPage from '../components/PaymentPage.vue';


const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,  // Correct component name
  },
  {
    path: '/locations',
    name: 'Locations',
    component: LocationPage,  // Correct component name
  },
  {
    path: '/booking',
    name: 'Booking',
    component: BookingPage,  // Correct component name
  },
  {
    path: '/payment',
    name: 'Payment',
    component: PaymentPage,  // Correct component name
  },
];

// Vue 3 requires using createRouter and createWebHistory instead of Vue.use(Router).
const router = createRouter({
  history: createWebHistory(),   
  routes,
});

export default router;
