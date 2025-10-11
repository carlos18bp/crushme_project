<template>
  <section class="notes-section">
    <!-- Section Header -->
    <div class="section-header">
      <!-- Primera fila: Título alineado a la derecha -->
      <div class="title-row">
        <h2 class="section-title">{{ $t('notes.title') }}</h2>
      </div>
      
      <!-- Segunda fila: Subtítulo alineado a la izquierda -->
      <div class="subtitle-row">
        <p class="section-subtitle">
          {{ $t('notes.subtitle') }}
        </p>
      </div>
      
      <!-- Tercera fila: Botón alineado a la izquierda -->
      <div class="button-row">
        <button class="secrets-button">
          {{ $t('notes.secretsButton') }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ $t('notes.loading') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <p>❌ {{ error }}</p>
      <button @click="crushStore.fetchRandomSevenCrushes()" class="retry-button">
        {{ $t('notes.tryAgain') }}
      </button>
    </div>

    <!-- Notes Grid -->
    <div v-else-if="notes.length > 0" class="notes-grid">
      <NoteCard
        v-for="note in notes"
        :key="note.id"
        :username="note.username"
        :note="note.note"
        :status="note.status"
        :profile-picture="note.profilePicture"
      />
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>{{ $t('notes.empty') }}</p>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import NoteCard from './NoteCard.vue'
import { useCrushStore } from '@/stores/modules/crushStore'

const crushStore = useCrushStore()

// Estados locales
const isLoading = ref(false)
const error = ref(null)

// Mapear los datos del API al formato esperado por NoteCard
const notes = computed(() => {
  if (!crushStore.randomSevenCrushes || crushStore.randomSevenCrushes.length === 0) {
    return []
  }
  
  return crushStore.randomSevenCrushes.map(crush => ({
    id: crush.id,
    username: crush.username,
    note: crush.note || 'No note available',
    status: crush.current_status || 'Offline',
    profilePicture: crush.profile_picture_url || crushStore.getDefaultAvatar()
  }))
})

// Cargar crushes al montar el componente
onMounted(async () => {
  // Solo cargar si no hay datos ya cargados
  if (crushStore.randomSevenCrushes.length === 0) {
    isLoading.value = true
    error.value = null
    
    try {
      await crushStore.fetchRandomSevenCrushes()
      console.log('✅ Crushes loaded for notes section:', notes.value.length)
    } catch (err) {
      error.value = err.message || 'Error loading crushes'
      console.error('❌ Error loading crushes for notes:', err)
    } finally {
      isLoading.value = false
    }
  }
})
</script>

<style scoped>
/* Notes Section Container */
.notes-section {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 80px 40px;
  background: transparent;
}

/* Section Header */
.section-header {
  display: flex;
  flex-direction: column;
  margin-bottom: 60px;
  gap: 24px;
}

/* Primera fila: Título alineado a la derecha */
.title-row {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

.section-title {
  font-family: 'Comfortaa', cursive;
  font-size: 2.5rem;
  font-weight: 700;
  color: #11181E;
  margin: 0;
  line-height: 1.2;
}

/* Segunda fila: Subtítulo alineado a la izquierda */
.subtitle-row {
  display: flex;
  justify-content: flex-start;
  width: 100%;
}

.section-subtitle {
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  font-weight: 400;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

/* Tercera fila: Botón alineado a la izquierda */
.button-row {
  display: flex;
  justify-content: flex-start;
  width: 100%;
}

.secrets-button {
  padding: 18px 48px;
  background: #475569;
  color: white;
  border: none;
  border-radius: 50px;
  font-family: 'Poppins', sans-serif;
  font-size: 1.25rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.secrets-button:hover {
  background: #334155;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.secrets-button:active {
  transform: translateY(0);
}

/* Notes Grid */
.notes-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 48px 32px;
  align-items: start;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(255, 43, 43, 0.2);
  border-top-color: rgb(255, 43, 43);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: rgba(0, 0, 0, 0.6);
}

/* Error State */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;
}

.error-state p {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: rgba(0, 0, 0, 0.6);
}

.retry-button {
  padding: 12px 24px;
  background: rgb(255, 43, 43);
  color: white;
  border: none;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-button:hover {
  background: rgb(220, 38, 38);
  transform: translateY(-2px);
}

.retry-button:active {
  transform: translateY(0);
}

/* Empty State */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.empty-state p {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: rgba(0, 0, 0, 0.5);
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .notes-section {
    padding: 60px 32px;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .notes-grid {
    gap: 40px 24px;
  }
}

@media (max-width: 768px) {
  .notes-section {
    padding: 48px 24px;
  }
  
  .section-header {
    margin-bottom: 40px;
    gap: 20px;
  }
  
  .section-title {
    font-size: 1.75rem;
  }
  
  .section-subtitle {
    font-size: 1.25rem;
  }
  
  .secrets-button {
    width: 100%;
    padding: 16px 36px;
    font-size: 1.125rem;
  }
  
  .notes-grid {
    gap: 32px;
  }
}

@media (max-width: 480px) {
  .notes-section {
    padding: 40px 16px;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
  
  .section-subtitle {
    font-size: 1.125rem;
  }
  
  .secrets-button {
    padding: 14px 32px;
    font-size: 1rem;
  }
}
</style>

