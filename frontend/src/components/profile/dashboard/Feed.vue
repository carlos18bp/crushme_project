<template>
  <div 
    class="rounded-lg md:rounded-xl border-2 border-gray-900 overflow-hidden"
    style="background-color: #FFDDDD;"
  >
    <!-- Feed Title with separator line -->
    <div class="px-3 sm:px-4 md:px-6 pt-3 sm:pt-4 md:pt-6 pb-2 sm:pb-3 md:pb-4">
      <h2 class="text-base sm:text-lg md:text-xl lg:text-2xl font-light text-gray-900 font-comfortaa">
        {{ $t('profileDashboard.feed.title') }}
      </h2>
    </div>
    
    <!-- Separator line (full width) -->
    <div class="border-b-2 border-gray-900"></div>
    
    <!-- Feed Items -->
    <div class="relative px-3 sm:px-4 md:px-6 pt-3 sm:pt-4 md:pt-6 pb-3 sm:pb-4 md:pb-6">
      <!-- Feed Item 1 -->
      <div class="flex items-start md:items-center gap-2 sm:gap-3 md:gap-4 mb-4 sm:mb-5 md:mb-6">
        <!-- Timeline -->
        <div class="flex flex-col items-center flex-shrink-0 relative">
          <div class="w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 rounded-full bg-yellow-400 border-3 border-orange-500 relative z-10"></div>
          <div class="absolute top-8 sm:top-10 md:top-12 w-0.5 h-full bg-gray-900" style="left: 50%; transform: translateX(-50%);"></div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 min-w-0">
          <p class="text-[10px] sm:text-xs md:text-sm font-comfortaa text-gray-900 leading-tight">
            You spoiled @Mia 💖 with a Clitoral Suction Toy 😱
          </p>
        </div>
        
        <!-- Time -->
        <span class="text-[9px] sm:text-xs text-gray-600 font-comfortaa flex-shrink-0">
          1 Hour ago
        </span>
      </div>

      <!-- Feed Item 2 -->
      <div class="flex items-start md:items-center gap-2 sm:gap-3 md:gap-4 mb-4 sm:mb-5 md:mb-6">
        <!-- Timeline -->
        <div class="flex flex-col items-center flex-shrink-0 relative">
          <div class="w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 rounded-full bg-blue-300 border-3 border-blue-500 relative z-10"></div>
          <div class="absolute top-8 sm:top-10 md:top-12 w-0.5 h-full bg-gray-900" style="left: 50%; transform: translateX(-50%);"></div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 min-w-0">
          <p class="text-[10px] sm:text-xs md:text-sm font-comfortaa text-gray-900 leading-tight">
            @Sofi wrote a new note in her diary 💌 → I wish I had soft lace tonight...
          </p>
        </div>
        
        <!-- Time -->
        <span class="text-[9px] sm:text-xs text-gray-600 font-comfortaa flex-shrink-0">
          2 Days ago
        </span>
      </div>

      <!-- Feed Item 3 -->
      <div class="flex items-start md:items-center gap-2 sm:gap-3 md:gap-4 mb-4 sm:mb-5 md:mb-6">
        <!-- Timeline -->
        <div class="flex flex-col items-center flex-shrink-0 relative">
          <div class="w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 rounded-full bg-blue-600 border-3 border-blue-800 relative z-10"></div>
          <div class="absolute top-8 sm:top-10 md:top-12 w-0.5 h-full bg-gray-900" style="left: 50%; transform: translateX(-50%);"></div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 min-w-0">
          <p class="text-[10px] sm:text-xs md:text-sm font-comfortaa text-gray-900 leading-tight">
            Your Crush @Eva just received your gift 🎁 and left you a thank you note 💕
          </p>
        </div>
        
        <!-- Time -->
        <span class="text-[9px] sm:text-xs text-gray-600 font-comfortaa flex-shrink-0">
          2 Days ago
        </span>
      </div>

      <!-- Feed Item 4 (último sin línea) -->
      <div class="flex items-start md:items-center gap-2 sm:gap-3 md:gap-4">
        <!-- Timeline -->
        <div class="flex flex-col items-center flex-shrink-0 relative">
          <div class="w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 rounded-full bg-yellow-300 border-3 border-yellow-500 relative z-10"></div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 min-w-0">
          <p class="text-[10px] sm:text-xs md:text-sm font-comfortaa text-gray-900 leading-tight">
            You update your profile information.
          </p>
        </div>
        
        <!-- Time -->
        <span class="text-[9px] sm:text-xs text-gray-600 font-comfortaa flex-shrink-0">
          3 Days ago
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
// Feed component
</script>

<style scoped>
.font-comfortaa {
  font-family: 'Comfortaa', cursive;
}

.border-3 {
  border-width: 3px;
}
</style>

