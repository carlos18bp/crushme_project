<template>
  <div class="max-w-[1600px] mx-auto py-12 md:py-16 px-4 md:px-8">
    <!-- Título de la sección -->
    <div class="mb-8 md:mb-12 text-left">
      <h2 class="font-comfortaa text-3xl md:text-4xl lg:text-5xl font-bold text-black m-0">
        {{ $t('faq.title') }}
      </h2>
    </div>

    <!-- Preguntas frecuentes -->
    <div class="flex flex-col gap-4 md:gap-6">
      <div 
        v-for="(faq, index) in faqs" 
        :key="index"
        class="w-full"
      >
        <button
          @click="toggleFaq(index)"
          class="w-full flex items-center justify-between px-6 md:px-8 py-4 md:py-6 bg-[rgba(157,81,255,0.16)] border-2 border-black rounded-xl cursor-pointer transition-all duration-300 text-left hover:bg-[rgba(157,81,255,0.24)] hover:-translate-y-0.5 hover:shadow-[0_4px_12px_rgba(157,81,255,0.2)]"
          :class="{ 'bg-[rgba(157,81,255,0.24)] rounded-b-none': openIndex === index }"
        >
          <span class="font-comfortaa text-base md:text-lg lg:text-xl font-semibold text-black/70 flex-1 pr-4">{{ faq.question }}</span>
          <span class="flex items-center justify-center text-black/70 transition-transform duration-300 flex-shrink-0" :class="{ 'rotate-180': openIndex === index }">
            <svg 
              width="24" 
              height="24" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              stroke-width="2" 
              stroke-linecap="round" 
              stroke-linejoin="round"
            >
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </span>
        </button>
        
        <div 
          class="overflow-hidden transition-all duration-400 max-h-0 opacity-0"
          :class="{ 'max-h-[500px] opacity-100': openIndex === index }"
        >
          <div class="bg-[rgba(157,81,255,0.08)] border-2 border-t-0 border-black rounded-b-xl px-6 md:px-8 py-4 md:py-6">
            <p class="font-poppins text-sm md:text-base leading-relaxed text-black/80 m-0">{{ faq.answer }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, tm } = useI18n()

// Estado para controlar qué pregunta está abierta
const openIndex = ref(null)

// Obtener preguntas traducidas - tm() es para obtener mensajes como objetos/arrays
const faqs = computed(() => tm('faq.questions'))

// Función para alternar la apertura/cierre de preguntas
const toggleFaq = (index) => {
  if (openIndex.value === index) {
    openIndex.value = null
  } else {
    openIndex.value = index
  }
}
</script>

<style scoped>
/* No custom styles needed - using Tailwind */
</style>

