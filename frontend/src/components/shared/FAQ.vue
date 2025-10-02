<template>
  <div class="faq-container">
    <!-- Título de la sección -->
    <div class="faq-header">
      <h2 class="faq-title">
        {{ $t('faq.title') }}
      </h2>
    </div>

    <!-- Preguntas frecuentes -->
    <div class="faq-list">
      <div 
        v-for="(faq, index) in faqs" 
        :key="index"
        class="faq-item"
      >
        <button
          @click="toggleFaq(index)"
          class="faq-question"
          :class="{ 'active': openIndex === index }"
        >
          <span class="faq-question-text">{{ faq.question }}</span>
          <span class="faq-icon" :class="{ 'rotate': openIndex === index }">
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
          class="faq-answer-wrapper"
          :class="{ 'open': openIndex === index }"
        >
          <div class="faq-answer">
            <p class="faq-answer-text">{{ faq.answer }}</p>
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
.faq-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 4rem 2rem;
}

.faq-header {
  margin-bottom: 3rem;
  text-align: left;
}

.faq-title {
  font-family: 'Comfortaa', cursive;
  font-size: 2.5rem;
  font-weight: 700;
  color: #000000;
  margin: 0;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.faq-item {
  width: 100%;
}

.faq-question {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  background: rgba(157, 81, 255, 0.16);
  border: 2px solid #000000;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.faq-question:hover {
  background: rgba(157, 81, 255, 0.24);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(157, 81, 255, 0.2);
}

.faq-question.active {
  background: rgba(157, 81, 255, 0.24);
  border-radius: 0.75rem 0.75rem 0 0;
}

.faq-question-text {
  font-family: 'Comfortaa', cursive;
  font-size: 1.25rem;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
  flex: 1;
  padding-right: 1rem;
}

.faq-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0, 0, 0, 0.7);
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.faq-icon.rotate {
  transform: rotate(180deg);
}

.faq-answer-wrapper {
  overflow: hidden;
  max-height: 0;
  transition: max-height 0.4s ease, opacity 0.3s ease;
  opacity: 0;
}

.faq-answer-wrapper.open {
  max-height: 500px;
  opacity: 1;
}

.faq-answer {
  background: rgba(157, 81, 255, 0.08);
  border: 2px solid #000000;
  border-top: none;
  border-radius: 0 0 0.75rem 0.75rem;
  padding: 1.5rem 2rem;
}

.faq-answer-text {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  line-height: 1.7;
  color: rgba(0, 0, 0, 0.8);
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .faq-container {
    padding: 2rem 1rem;
  }

  .faq-title {
    font-size: 1.75rem;
  }

  .faq-question {
    padding: 1.25rem 1.5rem;
  }

  .faq-question-text {
    font-size: 1rem;
  }

  .faq-answer {
    padding: 1.25rem 1.5rem;
  }

  .faq-answer-text {
    font-size: 0.9rem;
  }

  .faq-list {
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .faq-title {
    font-size: 1.5rem;
  }

  .faq-question {
    padding: 1rem 1.25rem;
  }

  .faq-question-text {
    font-size: 0.95rem;
  }

  .faq-answer {
    padding: 1rem 1.25rem;
  }
}
</style>

