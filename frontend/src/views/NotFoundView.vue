<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-brand-pink-lighter via-brand-purple-light/30 to-brand-blue-light/40 px-4 py-8">
    <div class="text-center max-w-2xl mx-auto">
      <!-- 404 Large Text -->
      <h1 class="font-comfortaa text-8xl md:text-9xl lg:text-[12rem] font-bold text-brand-pink-dark mb-4 md:mb-6 animate-bounce">
        404
      </h1>
      
      <!-- Title -->
      <h2 class="font-comfortaa text-2xl md:text-3xl lg:text-4xl font-bold text-brand-dark mb-4 md:mb-6">
        Page Not Found
      </h2>
      
      <!-- Description -->
      <p class="font-poppins text-base md:text-lg lg:text-xl text-gray-600 mb-6 md:mb-8 leading-relaxed">
        The page you're looking for doesn't exist or has been moved.
      </p>
      
      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
        <router-link 
          to="/" 
          class="w-full sm:w-auto px-8 py-3 bg-brand-blue-medium text-white font-poppins font-medium rounded-full transition-all duration-300 hover:bg-brand-blue-medium/90 hover:shadow-lg hover:-translate-y-0.5 no-underline text-center"
        >
          Go Back Home
        </router-link>
        
        <button 
          @click="goBack"
          class="w-full sm:w-auto px-8 py-3 bg-white/60 backdrop-blur-sm text-brand-dark font-poppins font-medium rounded-full transition-all duration-300 hover:bg-white/80 hover:shadow-lg hover:-translate-y-0.5 border-2 border-brand-dark/10"
        >
          Go Back
        </button>
      </div>
      
      <!-- Decorative Element -->
      <div class="mt-12 md:mt-16">
        <svg class="w-48 h-48 md:w-64 md:h-64 mx-auto opacity-30" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
          <path fill="#E9C3CD" d="M44.7,-76.4C58.8,-69.2,71.8,-59.1,79.6,-45.8C87.4,-32.6,90,-16.3,88.5,-0.9C87,14.6,81.4,29.2,73.1,42.8C64.8,56.4,53.8,69,40.5,77.1C27.2,85.2,11.6,88.8,-3.7,95.2C-19,101.6,-38,110.8,-52.4,104.2C-66.8,97.6,-76.6,75.2,-82.9,54.4C-89.2,33.6,-92,14.4,-90.3,-4.1C-88.6,-22.6,-82.4,-40.4,-72.8,-54.9C-63.2,-69.4,-50.2,-80.6,-35.8,-87.5C-21.4,-94.4,-5.6,-97,9.5,-91.3C24.6,-85.6,30.6,-83.6,44.7,-76.4Z" transform="translate(100 100)" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.back()
}
</script>

<style scoped>
/* No custom styles needed - using Tailwind */
</style>
