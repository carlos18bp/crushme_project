<template>
  <div class="min-h-screen relative overflow-hidden flex flex-col">
    <Navbar />
    
    <!-- Background Image -->
    <div 
      class="absolute inset-0 z-0"
      :style="{ 
        backgroundImage: `url(${backgroundImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }"
    ></div>

    <!-- Gradient Overlay -->
    <div class="absolute inset-0 z-0 bg-gradient-to-br from-brand-pink-lighter/30 via-brand-purple-light/20 to-brand-blue-light/30"></div>

    <!-- Content -->
    <div class="relative z-10 flex-1 flex items-center justify-center px-4 pt-32 md:pt-40 lg:pt-48 pb-8">
      <div class="w-full max-w-5xl">
        <!-- Contact Form Card -->
        <div class="bg-white/40 backdrop-blur-lg rounded-xl md:rounded-2xl shadow-2xl p-4 md:p-6 lg:p-8">
          <!-- Header -->
          <div class="flex items-center justify-between mb-4 md:mb-6">
            <h1 class="text-xl md:text-2xl lg:text-3xl font-bold text-brand-dark font-comfortaa">
              {{ $t('contact.title') }}
            </h1>
            <button 
              @click="goBack"
              class="p-2 hover:bg-brand-pink-light/30 rounded-full transition-colors duration-200 flex-shrink-0"
              :aria-label="$t('contact.goBack')"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5 md:w-6 md:h-6 text-brand-dark">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
              </svg>
            </button>
          </div>

          <!-- Form -->
          <form @submit.prevent="handleSubmit" class="space-y-3 md:space-y-4">
            <!-- To Field (Read-only) -->
            <div>
              <label class="block text-brand-dark font-poppins font-medium text-xs md:text-sm mb-1">
                {{ $t('contact.for') }}:
              </label>
              <div class="text-brand-dark font-poppins text-xs md:text-sm bg-white/20 rounded-lg px-3 py-2">
                BuyIt4me (team@buyit4me.com)
              </div>
            </div>

            <!-- From Field -->
            <div>
              <label for="email" class="block text-brand-dark font-poppins font-medium text-xs md:text-sm mb-1">
                {{ $t('contact.from') }}:
              </label>
              <input
                id="email"
                v-model="form.email"
                type="email"
                required
                :placeholder="$t('contact.emailPlaceholder')"
                class="w-full font-poppins !bg-transparent backdrop-blur-sm border-0 rounded-lg px-3 py-2 text-xs md:text-sm text-brand-dark placeholder-brand-dark/60 focus:outline-none focus:ring-2 focus:ring-brand-pink-dark/50 transition-all duration-200"
              />
            </div>

            <!-- Name Field -->
            <div>
              <label for="name" class="block text-brand-dark font-poppins font-medium text-xs md:text-sm mb-1">
                {{ $t('contact.name') }}:
              </label>
              <input
                id="name"
                v-model="form.name"
                type="text"
                required
                :placeholder="$t('contact.namePlaceholder')"
                class="w-full font-poppins !bg-transparent backdrop-blur-sm border-0 rounded-lg px-3 py-2 text-xs md:text-sm text-brand-dark placeholder-brand-dark/60 focus:outline-none focus:ring-2 focus:ring-brand-pink-dark/50 transition-all duration-200"
              />
            </div>

            <!-- Phone Field -->
            <div>
              <label for="phone" class="block text-brand-dark font-poppins font-medium text-xs md:text-sm mb-1">
                {{ $t('contact.number') }}:
              </label>
              <input
                id="phone"
                v-model="form.phone"
                type="tel"
                :placeholder="$t('contact.phonePlaceholder')"
                class="w-full font-poppins !bg-transparent backdrop-blur-sm border-0 rounded-lg px-3 py-2 text-xs md:text-sm text-brand-dark placeholder-brand-dark/60 focus:outline-none focus:ring-2 focus:ring-brand-pink-dark/50 transition-all duration-200"
              />
            </div>

            <!-- Subject Field -->
            <div>
              <label for="subject" class="block text-brand-dark font-poppins font-medium text-xs md:text-sm mb-1">
                {{ $t('contact.subject') }}:
              </label>
              <input
                id="subject"
                v-model="form.subject"
                type="text"
                required
                :placeholder="$t('contact.subjectPlaceholder')"
                class="w-full font-poppins !bg-transparent backdrop-blur-sm border-0 rounded-lg px-3 py-2 text-xs md:text-sm text-brand-dark placeholder-brand-dark/60 focus:outline-none focus:ring-2 focus:ring-brand-pink-dark/50 transition-all duration-200"
              />
            </div>

            <!-- Message Field -->
            <div>
              <label for="message" class="sr-only">
                {{ $t('contact.message') }}
              </label>
              <textarea
                id="message"
                v-model="form.message"
                rows="4"
                required
                :placeholder="$t('contact.messagePlaceholder')"
                class="w-full font-poppins !bg-transparent backdrop-blur-sm border-0 rounded-lg px-3 py-2 text-xs md:text-sm text-brand-dark placeholder-brand-dark/60 focus:outline-none focus:ring-2 focus:ring-brand-pink-dark/50 transition-all duration-200 resize-none"
              ></textarea>
            </div>

            <!-- Action Buttons -->
            <div class="flex flex-col sm:flex-row justify-end gap-2 md:gap-3 pt-2">
              <button
                type="button"
                @click="goBack"
                class="w-full sm:w-auto px-6 py-2 rounded-full text-xs md:text-sm text-brand-dark font-poppins font-medium hover:bg-white/40 transition-all duration-200 order-2 sm:order-1"
              >
                {{ $t('contact.cancel') }}
              </button>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="w-full sm:w-auto px-6 py-2 rounded-full text-xs md:text-sm bg-brand-blue-medium text-white font-poppins font-medium hover:bg-brand-blue-medium/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl order-1 sm:order-2"
              >
                {{ isSubmitting ? $t('contact.sending') : $t('contact.send') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useContactStore } from '@/stores/modules/contactStore';
import { useAlert } from '@/composables/useAlert';
import { useI18n } from 'vue-i18n';
import Navbar from '@/components/shared/Navbar.vue';
import Footer from '@/components/shared/Footer.vue';
import backgroundImage from '@/assets/backgrounds/background_1.png';

const router = useRouter();
const contactStore = useContactStore();
const { showSuccess, showError } = useAlert();
const { t } = useI18n();

const form = ref({
  email: '',
  name: '',
  phone: '',
  subject: '',
  message: ''
});

const isSubmitting = computed(() => contactStore.isSubmitting);

const goBack = () => {
  router.back();
};

const handleSubmit = async () => {
  // Clear previous messages
  contactStore.clearState();
  
  // Prepare data for API (map frontend fields to backend fields)
  const contactData = {
    email: form.value.email,
    nombre: form.value.name,
    numero: form.value.phone || '',
    asunto: form.value.subject,
    texto: form.value.message
  };
  
  try {
    const result = await contactStore.sendContactForm(contactData);
    
    if (result.success) {
      // Show success alert with SweetAlert2
      await showSuccess(
        contactStore.successMessage || 'Tu mensaje ha sido enviado exitosamente. Te responderemos pronto.'
      );
      
      // Clear form
      form.value = {
        email: '',
        name: '',
        phone: '',
        subject: '',
        message: ''
      };
    } else {
      // Show error alert with all error messages
      const errorMessage = contactStore.errorMessages.join('\n');
      await showError(
        errorMessage || 'Hubo un error al enviar el mensaje. Por favor intenta de nuevo.'
      );
    }
  } catch (error) {
    console.error('Error sending message:', error);
    await showError(
      'Ocurrió un error inesperado. Por favor intenta de nuevo.'
    );
  }
};
</script>

<style scoped>
/* Eliminar estilos de autocomplete del navegador (no se puede hacer con Tailwind) */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
  -webkit-box-shadow: 0 0 0 1000px transparent inset !important;
  box-shadow: 0 0 0 1000px transparent inset !important;
  -webkit-text-fill-color: #11181E !important;
  transition: background-color 5000s ease-in-out 0s;
}

textarea:-webkit-autofill,
textarea:-webkit-autofill:hover,
textarea:-webkit-autofill:focus,
textarea:-webkit-autofill:active {
  -webkit-box-shadow: 0 0 0 1000px transparent inset !important;
  box-shadow: 0 0 0 1000px transparent inset !important;
  -webkit-text-fill-color: #11181E !important;
  transition: background-color 5000s ease-in-out 0s;
}
</style>

