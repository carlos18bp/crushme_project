<template>
  <div class="product-detail-view">
    <h1>Product Detail</h1>
    <p>Product ID: {{ $route.params.id }}</p>
    <p>Product details will be here</p>
  </div>
</template>

<script setup>
// Product detail view component using Composition API
defineProps({
  id: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.product-detail-view {
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
