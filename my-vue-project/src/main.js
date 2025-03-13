import { createApp } from 'vue';
import App from './App.vue';
import router from './router';  // Import the router

// Create the app and use the router
createApp(App)
  .use(router)  // Use Vue Router
  .mount('#app');

