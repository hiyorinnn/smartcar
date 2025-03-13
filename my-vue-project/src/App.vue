<template>
  <div id="app">
    <!-- This is where the routed components will be rendered -->

    <!-- Static content in the App component -->
    <p>Hello</p>


    <!-- Button to navigate to the Payment page via router-link -->
    <router-link to="/payment">
      Go to Payment Page
    </router-link>

    <router-view></router-view> 
  </div>
</template>

<script>

export default {
  name: 'App',

};
</script>
