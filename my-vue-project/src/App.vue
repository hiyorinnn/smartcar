<template>
  <div id="app">
    <router-view></router-view> <!-- This is where the routed components will be rendered -->

    <!-- Using router-link to navigate to the Payment page -->
    <router-link to="/payment">
      Payment
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'App',
};
</script>
