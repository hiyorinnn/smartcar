<!-- HomePage.vue -->
<template>
  <div>
    <h1>{{ msg }}</h1>  <!-- Displaying the msg prop passed from App.vue -->
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  props: {
    msg: String  // Defining the 'msg' prop
  }
}
</script>

<style scoped>
/* Add your styles here */
</style>
