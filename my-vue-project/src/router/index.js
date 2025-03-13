import Vue from 'vue';
import Router from 'vue-router';

// Import the components/pages from the correct path
import HomePage from '../components/HomePage.vue';
import LocationPage from '../components/LocationPage.vue';
import BookingPage from '../components/BookingPage.vue';
import PaymentPage from '../components/PaymentPage.vue';

Vue.use(Router);

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

const router = new Router({
  routes, // Short for `routes: routes`
  mode: 'history', // This removes the hash (`#`) from the URL
});

export default router;
