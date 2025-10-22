<template>
  <div class="currency-toggle">
    <button 
      @click="toggleCurrency"
      class="currency-btn"
      :title="`Switch to ${currentCurrency === 'COP' ? 'USD' : 'COP'}`"
    >
      <span class="currency-icon">💱</span>
      <span class="currency-text">{{ currentCurrency }}</span>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useCurrencyStore } from '@/stores/modules/currencyStore';

const currencyStore = useCurrencyStore();

const currentCurrency = computed(() => currencyStore.currentCurrency);

function toggleCurrency() {
  currencyStore.toggleCurrency();
  // Optional: Show toast notification
  console.log(`Currency changed to ${currencyStore.currentCurrency}`);
}
</script>

<style scoped>
.currency-toggle {
  display: inline-flex;
  align-items: center;
}

.currency-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
  color: #374151;
}

.currency-btn:hover {
  background-color: #e5e7eb;
  border-color: #9ca3af;
}

.currency-icon {
  font-size: 1.2rem;
}

.currency-text {
  font-size: 0.875rem;
  font-weight: 600;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .currency-btn {
    background-color: #374151;
    border-color: #4b5563;
    color: #f3f4f6;
  }

  .currency-btn:hover {
    background-color: #4b5563;
    border-color: #6b7280;
  }
}
</style>
