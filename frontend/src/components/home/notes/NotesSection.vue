<template>
  <section class="w-full max-w-[1600px] mx-auto py-12 md:py-16 lg:py-20 px-6 md:px-10 bg-transparent">
    <!-- Section Header -->
    <div class="flex flex-col mb-12 md:mb-16 gap-5 md:gap-6">
      <!-- Primera fila: Título alineado a la derecha -->
      <div class="flex justify-start lg:justify-end w-full">
        <h2 class="font-comfortaa text-2xl md:text-3xl lg:text-4xl font-bold text-[#11181E] m-0 leading-tight">{{ $t('notes.title') }}</h2>
      </div>
      
      <!-- Segunda fila: Subtítulo alineado a la izquierda -->
      <div class="flex justify-start w-full">
        <p class="font-poppins text-lg md:text-xl lg:text-2xl font-normal text-slate-500 m-0 leading-relaxed">
          {{ $t('notes.subtitle') }}
        </p>
      </div>
      
      <!-- Tercera fila: Botón alineado a la izquierda -->
      <div class="flex justify-start w-full">
        <button 
          @click="goToMyDiaries"
          class="px-8 md:px-10 lg:px-12 py-3 md:py-4 lg:py-[1.125rem] bg-slate-600 text-white border-none rounded-full font-poppins text-base md:text-lg lg:text-xl font-medium cursor-pointer transition-all duration-300 whitespace-nowrap hover:bg-slate-700 hover:-translate-y-0.5 hover:shadow-[0_8px_16px_rgba(0,0,0,0.15)] active:translate-y-0 w-full sm:w-auto"
        >
          {{ $t('notes.secretsButton') }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-16 md:py-20 gap-4">
      <div class="w-12 h-12 border-4 border-red-400/20 border-t-red-500 rounded-full animate-spin"></div>
      <p class="font-poppins text-base text-black/60">{{ $t('notes.loading') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex flex-col items-center justify-center py-16 md:py-20 gap-4">
      <p class="font-poppins text-base text-black/60">❌ {{ error }}</p>
      <button @click="crushStore.fetchRandomSevenCrushes()" class="px-6 py-3 bg-red-500 text-white border-none rounded-lg font-poppins text-sm font-medium cursor-pointer transition-all duration-200 hover:bg-red-600 hover:-translate-y-0.5 active:translate-y-0">
        {{ $t('notes.tryAgain') }}
      </button>
    </div>

    <!-- Notes Grid -->
    <div v-else-if="notes.length > 0" class="flex flex-wrap justify-center gap-8 md:gap-10 lg:gap-12 items-start">
      <NoteCard
        v-for="(note, index) in notes"
        :key="note.id"
        v-show="index < 3 || isDesktop"
        :username="note.username"
        :note="note.note"
        :status="note.status"
        :profile-picture="note.profilePicture"
      />
    </div>

    <!-- Empty State -->
    <div v-else class="flex items-center justify-center py-16 md:py-20">
      <p class="font-poppins text-base text-black/50">{{ $t('notes.empty') }}</p>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import NoteCard from './NoteCard.vue'
import { useCrushStore } from '@/stores/modules/crushStore'
import { useAuthStore } from '@/stores/modules/authStore'

const router = useRouter()
const crushStore = useCrushStore()
const authStore = useAuthStore()

// Estados locales
const isLoading = ref(false)
const error = ref(null)

// Detectar si es desktop
const isDesktop = ref(window.innerWidth >= 1024)

const handleResize = () => {
  isDesktop.value = window.innerWidth >= 1024
}

// Ir a la vista de Diaries del usuario actual
const goToMyDiaries = () => {
  console.log('🔄 Go to my diaries clicked')
  console.log('Auth state:', { isLoggedIn: authStore.isLoggedIn, username: authStore.user?.username })
  
  if (authStore.isLoggedIn && authStore.user?.username) {
    console.log('✅ Navigating to:', `/diaries/@${authStore.user.username}`)
    router.push(`/diaries/@${authStore.user.username}`)
  } else {
    // Si no está logueado, ir a Diaries general
    console.log('⚠️ Not logged in, going to general diaries')
    router.push('/diaries')
  }
}

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
  // Agregar listener de resize
  window.addEventListener('resize', handleResize)
  
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

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* No custom styles needed - using Tailwind */
</style>

