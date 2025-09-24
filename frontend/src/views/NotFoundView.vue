<template>
  <div class="not-found-view">
    <h1>404 - Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <router-link to="/" class="back-home">Go Back Home</router-link>
  </div>
</template>

<script setup>
// Not found view component using Composition API
</script>

<style scoped>
.not-found-view {
  padding: 2rem;
  text-align: center;
}

h1 {
  color: #e74c3c;
  margin-bottom: 1rem;
}

p {
  color: #7f8c8d;
  margin-bottom: 2rem;
}

.back-home {
  color: #3498db;
  text-decoration: none;
  font-weight: bold;
}

.back-home:hover {
  text-decoration: underline;
}
</style>
