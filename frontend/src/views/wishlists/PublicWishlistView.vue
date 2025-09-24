<template>
  <div class="public-wishlist-view">
    <h1>Shared Wishlist</h1>
    <p>Wishlist UUID: {{ $route.params.uuid }}</p>
    <p>Public wishlist will be here</p>
  </div>
</template>

<script setup>
// Public wishlist view component using Composition API
defineProps({
  uuid: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.public-wishlist-view {
  padding: 2rem;
  text-align: center;
}

h1 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

p {
  color: #7f8c8d;
}
</style>
