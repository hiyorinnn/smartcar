<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/locations">Locations</router-link> |
      <router-link to="/booking">Booking</router-link> |
      <router-link to="/payment">Payment</router-link>
    </nav>

    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

nav {
  padding: 10px;
  background: #f8f9fa;
}

nav a {
  margin: 0 10px;
  text-decoration: none;
  color: #007bff;
}

nav a:hover {
  text-decoration: underline;
}
</style>
