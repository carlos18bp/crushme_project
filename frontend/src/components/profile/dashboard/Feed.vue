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
    
    <!-- Loading State -->
    <div v-if="profileStore.isLoadingFeed" class="px-3 sm:px-4 md:px-6 py-6 text-center">
      <p class="text-sm text-gray-600 font-comfortaa">{{ $t('profileDashboard.feed.loading') }}</p>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="!profileStore.hasFeedItems" class="px-3 sm:px-4 md:px-6 py-6 text-center">
      <p class="text-sm text-gray-600 font-comfortaa">{{ $t('profileDashboard.feed.empty') }}</p>
    </div>
    
    <!-- Feed Items -->
    <div v-else class="relative px-3 sm:px-4 md:px-6 pt-3 sm:pt-4 md:pt-6 pb-3 sm:pb-4 md:pb-6">
      <div 
        v-for="(item, index) in profileStore.feedItems" 
        :key="item.id"
        class="flex items-start md:items-center gap-2 sm:gap-3 md:gap-4"
        :class="{ 'mb-4 sm:mb-5 md:mb-6': index < profileStore.feedItems.length - 1 }"
      >
        <!-- Timeline -->
        <div :class="item.style" class="flex flex-col items-center flex-shrink-0 relative">
          <div class="timeline-circle w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 rounded-full border-3 relative z-10"></div>
          <!-- Línea conectora (solo si no es el último item) -->
          <div 
            v-if="index < profileStore.feedItems.length - 1"
            :class="getNextItemStyle(index)"
            class="absolute top-8 sm:top-10 md:top-12 w-0.5 h-full" 
            style="left: 50%; transform: translateX(-50%);"
          >
            <div class="timeline-line w-full h-full"></div>
          </div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 min-w-0">
          <p class="text-[10px] sm:text-xs md:text-sm font-comfortaa text-gray-900 leading-tight">
            {{ item.text }}
          </p>
        </div>
        
        <!-- Time -->
        <span class="text-[9px] sm:text-xs text-gray-600 font-comfortaa flex-shrink-0">
          {{ getRelativeTime(item.created_at) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useProfileStore } from '@/stores/modules/profileStore';
import { useI18nStore } from '@/stores/modules/i18nStore';

const profileStore = useProfileStore();
const i18nStore = useI18nStore();

/**
 * Get the style class for the next item's line
 * The line should have the border color of the NEXT circle
 */
function getNextItemStyle(currentIndex) {
  const nextIndex = currentIndex + 1;
  if (nextIndex < profileStore.feedItems.length) {
    return profileStore.feedItems[nextIndex].style;
  }
  return '';
}

/**
 * Calculate relative time from created_at timestamp
 * @param {string} timestamp - ISO timestamp
 * @returns {string} - Relative time string
 */
function getRelativeTime(timestamp) {
  const now = new Date();
  const created = new Date(timestamp);
  const diffMs = now - created;
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);
  const diffWeeks = Math.floor(diffDays / 7);
  const diffMonths = Math.floor(diffDays / 30);
  const diffYears = Math.floor(diffDays / 365);

  const locale = i18nStore.locale;

  if (diffSeconds < 60) {
    return locale === 'es' ? 'Justo ahora' : 'Just now';
  } else if (diffMinutes < 60) {
    return locale === 'es' 
      ? `Hace ${diffMinutes} ${diffMinutes === 1 ? 'minuto' : 'minutos'}`
      : `${diffMinutes} ${diffMinutes === 1 ? 'minute' : 'minutes'} ago`;
  } else if (diffHours < 24) {
    return locale === 'es'
      ? `Hace ${diffHours} ${diffHours === 1 ? 'hora' : 'horas'}`
      : `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`;
  } else if (diffDays < 7) {
    return locale === 'es'
      ? `Hace ${diffDays} ${diffDays === 1 ? 'día' : 'días'}`
      : `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ago`;
  } else if (diffWeeks < 4) {
    return locale === 'es'
      ? `Hace ${diffWeeks} ${diffWeeks === 1 ? 'semana' : 'semanas'}`
      : `${diffWeeks} ${diffWeeks === 1 ? 'week' : 'weeks'} ago`;
  } else if (diffMonths < 12) {
    return locale === 'es'
      ? `Hace ${diffMonths} ${diffMonths === 1 ? 'mes' : 'meses'}`
      : `${diffMonths} ${diffMonths === 1 ? 'month' : 'months'} ago`;
  } else {
    return locale === 'es'
      ? `Hace ${diffYears} ${diffYears === 1 ? 'año' : 'años'}`
      : `${diffYears} ${diffYears === 1 ? 'year' : 'years'} ago`;
  }
}

// Fetch feed on component mount
onMounted(async () => {
  await profileStore.fetchMyFeed();
});
</script>

<style scoped>
.font-comfortaa {
  font-family: 'Comfortaa', cursive;
}

.border-3 {
  border-width: 3px;
}

/* Timeline Styles - CrushMe Brand Colors */

/* Style 1: Pink Dream */
.timeline-pink-dream .timeline-circle {
  background-color: #FF3FD5; /* brand-pink */
  border-color: #BF5E81; /* brand-pink-dark */
}

.timeline-pink-dream .timeline-line {
  background-color: #BF5E81; /* brand-pink-dark */
}

/* Style 2: Purple Passion */
.timeline-purple-passion .timeline-circle {
  background-color: #DA9DFF; /* brand-purple-light */
  border-color: #9B5FC7; /* purple darker */
}

.timeline-purple-passion .timeline-line {
  background-color: #9B5FC7;
}

/* Style 3: Rose Blush */
.timeline-rose-blush .timeline-circle {
  background-color: #FAF3F3; /* brand-pink-lighter */
  border-color: #E9C3CD; /* brand-pink-light */
}

.timeline-rose-blush .timeline-line {
  background-color: #E9C3CD;
}

/* Style 4: Ocean Blue */
.timeline-ocean-blue .timeline-circle {
  background-color: #A4C1D0; /* brand-blue-light */
  border-color: #406582; /* brand-blue-medium */
}

.timeline-ocean-blue .timeline-line {
  background-color: #406582;
}

/* Style 5: Coral Sunset */
.timeline-coral-sunset .timeline-circle {
  background-color: #D689A2; /* brand-pink-medium */
  border-color: #BF5E81; /* brand-pink-dark */
}

.timeline-coral-sunset .timeline-line {
  background-color: #BF5E81;
}

/* Style 6: Midnight Rose */
.timeline-midnight-rose .timeline-circle {
  background-color: #BF5E81; /* brand-pink-dark */
  border-color: #11181E; /* brand-dark */
}

.timeline-midnight-rose .timeline-line {
  background-color: #11181E;
}
</style>

