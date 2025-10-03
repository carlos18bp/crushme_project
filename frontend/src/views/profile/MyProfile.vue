<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <form @submit.prevent="handleSubmit" class="space-y-10">
      
      <!-- Shipping info section -->
      <div>
        <h2 class="text-2xl font-semibold text-gray-900 mb-6 font-comfortaa">
          {{ $t('profile.form.shippingDetails.title') }}
        </h2>

        <div class="space-y-6">
          <!-- First name & Last name -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label for="first_name" class="block text-sm font-medium text-gray-900 mb-2">
                {{ $t('profile.form.basicInfo.firstName') }} <span class="text-red-500">*</span>
              </label>
              <input
                id="first_name"
                v-model="formData.first_name"
                type="text"
                :placeholder="$t('profile.form.placeholders.firstName')"
                class="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
                required
              />
            </div>

            <div>
              <label for="last_name" class="block text-sm font-medium text-gray-900 mb-2">
                {{ $t('profile.form.basicInfo.lastName') }}
              </label>
              <input
                id="last_name"
                v-model="formData.last_name"
                type="text"
                :placeholder="$t('profile.form.placeholders.lastName')"
                class="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
              />
            </div>
          </div>

          <!-- Work email & Phone -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label for="email" class="block text-sm font-medium text-gray-900 mb-2">
                {{ $t('profile.form.basicInfo.email') }} <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <input
                  id="email"
                  v-model="formData.email"
                  type="email"
                  :placeholder="$t('profile.form.placeholders.email')"
                  class="block w-full rounded-lg border border-brand-pink-dark pl-11 pr-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
                  required
                />
              </div>
            </div>

            <div>
              <label for="phone" class="block text-sm font-medium text-gray-900 mb-2">
                {{ $t('profile.form.basicInfo.phone') }}
              </label>
              <div class="flex gap-2">
                <select
                  v-model="formData.phoneCode"
                  class="rounded-lg border border-gray-300 px-3 py-3 text-gray-900 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
                >
                  <option v-for="country in countryCodes" :key="country.code" :value="country.dial_code">
                    {{ country.flag }} {{ country.dial_code }}
                  </option>
                </select>
                <input
                  id="phone"
                  v-model="formData.phone"
                  type="tel"
                  :placeholder="$t('profile.form.placeholders.phone')"
                  class="flex-1 block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
                />
              </div>
            </div>
          </div>

          <!-- Country or Region -->
          <div>
            <label for="country" class="block text-sm font-medium text-gray-900 mb-2">
              {{ $t('profile.form.shippingDetails.country') }}
            </label>
            <select
              id="country"
              v-model="formData.country"
              @change="onCountryChange"
              class="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
            >
              <option value="">{{ $t('profile.form.placeholders.selectCountry') }}</option>
              <option v-for="country in countries" :key="country.isoCode" :value="country.isoCode">
                {{ country.flag }} {{ country.name }}
              </option>
            </select>
          </div>

          <!-- State & ZIP code -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label for="state" class="block text-sm font-medium text-gray-900 mb-2">
                {{ $t('profile.form.shippingDetails.state') }}
              </label>
              <select
                id="state"
                v-model="formData.state"
                :disabled="!formData.country"
                class="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                <option value="">{{ formData.country ? $t('profile.form.placeholders.selectState') : $t('profile.form.placeholders.selectCountry') }}</option>
                <option v-for="state in availableStates" :key="state.isoCode" :value="state.name">
                  {{ state.name }}
                </option>
              </select>
            </div>

            <div>
              <label for="postal_code" class="block text-sm font-medium text-gray-900 mb-2">
                {{ $t('profile.form.shippingDetails.postalCode') }}
              </label>
              <input
                id="postal_code"
                v-model="formData.postal_code"
                type="text"
                :placeholder="$t('profile.form.placeholders.postalCode')"
                class="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
              />
            </div>
          </div>

          <!-- City -->
          <div>
            <label for="city" class="block text-sm font-medium text-gray-900 mb-2">
              {{ $t('profile.form.shippingDetails.city') }}
            </label>
            <input
              id="city"
              v-model="formData.city"
              type="text"
              :placeholder="$t('profile.form.placeholders.city')"
              class="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
            />
          </div>

          <!-- Your address -->
          <div>
            <label class="block text-sm font-medium text-gray-900 mb-2">
              {{ $t('profile.form.shippingDetails.addressLine1') }} <span class="text-red-500">*</span>
            </label>
            
            <div class="space-y-3">
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <input
                  v-model="formData.address_line1"
                  type="text"
                  :placeholder="$t('profile.form.placeholders.addressLine1')"
                  class="block w-full rounded-lg border border-gray-300 pl-11 pr-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
                  required
                />
              </div>

              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <input
                  v-model="formData.address_line2"
                  type="text"
                  :placeholder="$t('profile.form.placeholders.addressLine2')"
                  class="block w-full rounded-lg border border-gray-300 pl-11 pr-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
                />
              </div>
            </div>
          </div>

          <!-- Additional address details -->
          <div>
            <label for="additional_details" class="block text-sm font-medium text-gray-900 mb-2">
              {{ $t('profile.form.shippingDetails.additionalDetails') }}
            </label>
            <textarea
              id="additional_details"
              v-model="formData.additional_details"
              rows="4"
              :placeholder="$t('profile.form.placeholders.additionalDetails')"
              class="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors resize-none"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Public profile information section -->
      <div>
        <h2 class="text-2xl font-semibold text-gray-900 mb-6 font-comfortaa">
          {{ $t('profile.form.publicProfile.title') }}
        </h2>

        <div class="space-y-6">
          <!-- Username -->
          <div class="max-w-md">
            <label for="username" class="block text-sm font-medium text-gray-900 mb-2">
              {{ $t('profile.form.basicInfo.username') }} <span class="text-red-500">*</span>
            </label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              :placeholder="$t('profile.form.placeholders.username')"
              class="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
              required
            />
          </div>

          <!-- About yourself -->
          <div>
            <label for="about" class="block text-sm font-medium text-gray-900 mb-2">
              {{ $t('profile.form.basicInfo.about') }}
            </label>
            <textarea
              id="about"
              v-model="formData.about"
              rows="4"
              :placeholder="$t('profile.form.placeholders.about')"
              class="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors resize-none"
            ></textarea>
          </div>

          <!-- Gallery -->
          <div>
            <label class="block text-sm font-medium text-gray-900 mb-2">
              {{ $t('profile.form.gallery.title') }}
            </label>
            
            <!-- Upload area -->
            <div
              @dragover.prevent
              @drop.prevent="handleFileDrop"
              class="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-brand-pink-dark transition-colors cursor-pointer"
              @click="$refs.fileInput.click()"
            >
              <div class="flex flex-col items-center">
                <svg class="w-12 h-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <button
                  type="button"
                  class="px-4 py-2 bg-white border border-brand-pink-dark rounded-lg text-sm font-medium text-brand-pink-dark hover:bg-brand-pink-lighter transition-colors mb-2"
                >
                  {{ $t('profile.form.gallery.selectFiles') }}
                </button>
                <p class="text-sm text-gray-500">{{ $t('profile.form.gallery.dropzone') }}</p>
                <p class="text-xs text-gray-400 mt-2">{{ $t('profile.form.gallery.requirements') }}</p>
              </div>
              <input
                ref="fileInput"
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/gif"
                multiple
                class="hidden"
                @change="handleFileSelect"
                :key="fileInputKey"
              />
            </div>

            <!-- Existing gallery photos -->
            <div v-if="existingPhotos.length > 0" class="mb-4">
              <h4 class="text-sm font-medium text-gray-700 mb-3">{{ $t('profile.form.gallery.currentPhotos') }}</h4>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                <div
                  v-for="photo in existingPhotos"
                  :key="photo.id"
                  class="relative group"
                >
                  <img
                    :src="getImageUrl(photo.image)"
                    :alt="photo.caption || 'Gallery photo'"
                    class="w-full h-32 object-cover rounded-lg border border-gray-200"
                  />
                  <div class="absolute top-2 right-2 flex gap-1">
                    <span
                      v-if="photo.is_profile_picture"
                      class="px-2 py-1 bg-brand-pink-dark text-white text-xs font-medium rounded-full"
                    >
                      Profile
                    </span>
                    <button
                      type="button"
                      @click="removeExistingPhoto(photo.id)"
                      class="p-1.5 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <p v-if="photo.caption" class="mt-1 text-xs text-gray-600 truncate">{{ photo.caption }}</p>
                </div>
              </div>
            </div>

            <!-- Uploaded files (new photos to upload) -->
            <div v-if="uploadedFiles.length > 0" class="mt-4">
              <h4 class="text-sm font-medium text-gray-700 mb-3">{{ $t('profile.form.gallery.newPhotos') }}</h4>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div
                  v-for="(file, index) in uploadedFiles"
                  :key="index"
                  class="flex items-center gap-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200"
                >
                  <div class="flex-shrink-0 w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">{{ file.name }}</p>
                    <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
                  </div>
                  <button
                    type="button"
                    @click="removeFile(index)"
                    class="flex-shrink-0 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Note -->
          <div>
            <label for="note" class="block text-sm font-medium text-gray-900 mb-2">
              {{ $t('profile.form.basicInfo.note') }}
            </label>
            <textarea
              id="note"
              v-model="formData.note"
              rows="4"
              :placeholder="$t('profile.form.placeholders.note')"
              class="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors resize-none"
            ></textarea>
          </div>

          <!-- Currently Status -->
          <div class="max-w-xl">
            <label for="current_status" class="block text-sm font-medium text-gray-900 mb-2">
              {{ $t('profile.form.basicInfo.currentStatus') }}
            </label>
            <input
              id="current_status"
              v-model="formData.current_status"
              type="text"
              :placeholder="$t('profile.form.placeholders.currentStatus')"
              class="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
            />
          </div>

          <!-- Linktree -->
          <div>
            <div class="flex items-center gap-2 mb-3">
              <label class="block text-sm font-medium text-gray-900">
                {{ $t('profile.form.linktree.title') }}
              </label>
              <button
                type="button"
                @click="addLink"
                class="w-6 h-6 bg-brand-pink-dark rounded-full flex items-center justify-center text-white hover:bg-brand-pink-medium transition-colors shadow-sm"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
              </button>
            </div>

            <div v-for="(link, index) in formData.links" :key="index" class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500 text-sm">
                  https://
                </div>
                <input
                  v-model="link.url"
                  type="text"
                  :placeholder="$t('profile.form.linktree.urlPlaceholder')"
                  class="block w-full rounded-lg border border-gray-300 pl-20 pr-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
                />
              </div>
              <div class="flex gap-2">
                <input
                  v-model="link.title"
                  type="text"
                  :placeholder="$t('profile.form.linktree.titlePlaceholder')"
                  class="flex-1 block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
                />
                <button
                  v-if="formData.links.length > 1"
                  type="button"
                  @click="removeLink(index)"
                  class="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Submit button -->
      <div>
        <button
          type="submit"
          :disabled="isLoading"
          class="px-8 py-3 bg-brand-pink-dark text-white font-medium rounded-full hover:bg-brand-pink-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-comfortaa shadow-md"
        >
          {{ isLoading ? $t('profile.form.buttons.loading') : $t('profile.form.buttons.save') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProfileStore } from '@/stores/modules/profileStore'
import { useAuthStore } from '@/stores/modules/authStore'
import { Country, State } from 'country-state-city'

const profileStore = useProfileStore()
const authStore = useAuthStore()

const isLoading = ref(false)
const uploadedFiles = ref([])
const existingPhotos = ref([])
const photosToDelete = ref([])
const fileInputKey = ref(0)

// Get all countries with flags
const countries = Country.getAllCountries().map(country => ({
  ...country,
  flag: country.flag || '🏳️'
}))

// Computed property for available states based on selected country
const availableStates = computed(() => {
  if (!formData.value.country) return []
  return State.getStatesOfCountry(formData.value.country)
})

const countryCodes = [
  { code: 'US', dial_code: '+1', flag: '🇺🇸', name: 'United States' },
  { code: 'CA', dial_code: '+1', flag: '🇨🇦', name: 'Canada' },
  { code: 'MX', dial_code: '+52', flag: '🇲🇽', name: 'Mexico' },
  { code: 'AR', dial_code: '+54', flag: '🇦🇷', name: 'Argentina' },
  { code: 'BR', dial_code: '+55', flag: '🇧🇷', name: 'Brazil' },
  { code: 'CL', dial_code: '+56', flag: '🇨🇱', name: 'Chile' },
  { code: 'CO', dial_code: '+57', flag: '🇨🇴', name: 'Colombia' },
  { code: 'PE', dial_code: '+51', flag: '🇵🇪', name: 'Peru' },
  { code: 'VE', dial_code: '+58', flag: '🇻🇪', name: 'Venezuela' },
  { code: 'EC', dial_code: '+593', flag: '🇪🇨', name: 'Ecuador' },
  { code: 'BO', dial_code: '+591', flag: '🇧🇴', name: 'Bolivia' },
  { code: 'PY', dial_code: '+595', flag: '🇵🇾', name: 'Paraguay' },
  { code: 'UY', dial_code: '+598', flag: '🇺🇾', name: 'Uruguay' },
  { code: 'ES', dial_code: '+34', flag: '🇪🇸', name: 'Spain' },
  { code: 'FR', dial_code: '+33', flag: '🇫🇷', name: 'France' },
  { code: 'DE', dial_code: '+49', flag: '🇩🇪', name: 'Germany' },
  { code: 'IT', dial_code: '+39', flag: '🇮🇹', name: 'Italy' },
  { code: 'GB', dial_code: '+44', flag: '🇬🇧', name: 'United Kingdom' },
  { code: 'PT', dial_code: '+351', flag: '🇵🇹', name: 'Portugal' },
  { code: 'NL', dial_code: '+31', flag: '🇳🇱', name: 'Netherlands' },
  { code: 'BE', dial_code: '+32', flag: '🇧🇪', name: 'Belgium' },
  { code: 'CH', dial_code: '+41', flag: '🇨🇭', name: 'Switzerland' },
  { code: 'AT', dial_code: '+43', flag: '🇦🇹', name: 'Austria' },
  { code: 'SE', dial_code: '+46', flag: '🇸🇪', name: 'Sweden' },
  { code: 'NO', dial_code: '+47', flag: '🇳🇴', name: 'Norway' },
  { code: 'DK', dial_code: '+45', flag: '🇩🇰', name: 'Denmark' },
  { code: 'FI', dial_code: '+358', flag: '🇫🇮', name: 'Finland' },
  { code: 'PL', dial_code: '+48', flag: '🇵🇱', name: 'Poland' },
  { code: 'CZ', dial_code: '+420', flag: '🇨🇿', name: 'Czech Republic' },
  { code: 'HU', dial_code: '+36', flag: '🇭🇺', name: 'Hungary' },
  { code: 'RO', dial_code: '+40', flag: '🇷🇴', name: 'Romania' },
  { code: 'GR', dial_code: '+30', flag: '🇬🇷', name: 'Greece' },
  { code: 'IE', dial_code: '+353', flag: '🇮🇪', name: 'Ireland' },
  { code: 'RU', dial_code: '+7', flag: '🇷🇺', name: 'Russia' },
  { code: 'UA', dial_code: '+380', flag: '🇺🇦', name: 'Ukraine' },
  { code: 'CN', dial_code: '+86', flag: '🇨🇳', name: 'China' },
  { code: 'JP', dial_code: '+81', flag: '🇯🇵', name: 'Japan' },
  { code: 'KR', dial_code: '+82', flag: '🇰🇷', name: 'South Korea' },
  { code: 'IN', dial_code: '+91', flag: '🇮🇳', name: 'India' },
  { code: 'PK', dial_code: '+92', flag: '🇵🇰', name: 'Pakistan' },
  { code: 'BD', dial_code: '+880', flag: '🇧🇩', name: 'Bangladesh' },
  { code: 'PH', dial_code: '+63', flag: '🇵🇭', name: 'Philippines' },
  { code: 'VN', dial_code: '+84', flag: '🇻🇳', name: 'Vietnam' },
  { code: 'TH', dial_code: '+66', flag: '🇹🇭', name: 'Thailand' },
  { code: 'MY', dial_code: '+60', flag: '🇲🇾', name: 'Malaysia' },
  { code: 'SG', dial_code: '+65', flag: '🇸🇬', name: 'Singapore' },
  { code: 'ID', dial_code: '+62', flag: '🇮🇩', name: 'Indonesia' },
  { code: 'AU', dial_code: '+61', flag: '🇦🇺', name: 'Australia' },
  { code: 'NZ', dial_code: '+64', flag: '🇳🇿', name: 'New Zealand' },
  { code: 'ZA', dial_code: '+27', flag: '🇿🇦', name: 'South Africa' },
  { code: 'EG', dial_code: '+20', flag: '🇪🇬', name: 'Egypt' },
  { code: 'NG', dial_code: '+234', flag: '🇳🇬', name: 'Nigeria' },
  { code: 'KE', dial_code: '+254', flag: '🇰🇪', name: 'Kenya' },
  { code: 'IL', dial_code: '+972', flag: '🇮🇱', name: 'Israel' },
  { code: 'SA', dial_code: '+966', flag: '🇸🇦', name: 'Saudi Arabia' },
  { code: 'AE', dial_code: '+971', flag: '🇦🇪', name: 'United Arab Emirates' },
  { code: 'TR', dial_code: '+90', flag: '🇹🇷', name: 'Turkey' }
]

const formData = ref({
  // Shipping info
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  phoneCode: '+1',
  country: '',
  city: '',
  state: '',
  postal_code: '',
  address_line1: '',
  address_line2: '',
  additional_details: '',
  
  // Public profile
  username: '',
  about: '',
  note: '',
  current_status: '',
  links: [{ url: '', title: '' }]
})

onMounted(async () => {
  // Cargar datos del perfil
  await profileStore.fetchProfile()
  
  if (profileStore.profile) {
    const profile = profileStore.profile
    const defaultAddr = profileStore.defaultAddress
    
    // Llenar datos básicos
    formData.value.first_name = profile.first_name || ''
    formData.value.last_name = profile.last_name || ''
    formData.value.email = profile.email || ''
    formData.value.phone = profile.phone || ''
    formData.value.username = profile.username || ''
    formData.value.about = profile.about || ''
    formData.value.note = profile.note || ''
    formData.value.current_status = profile.current_status || ''
    
    // Llenar dirección por defecto
    if (defaultAddr) {
      // Support both naming conventions (with underscore and without)
      formData.value.address_line1 = defaultAddr.address_line1 || defaultAddr.address_line_1 || ''
      formData.value.address_line2 = defaultAddr.address_line2 || defaultAddr.address_line_2 || ''
      formData.value.city = defaultAddr.city || ''
      formData.value.state = defaultAddr.state || ''
      formData.value.postal_code = defaultAddr.postal_code || defaultAddr.zip_code || ''
      formData.value.additional_details = defaultAddr.additional_details || ''
      
      // Find country by name and set isoCode
      if (defaultAddr.country) {
        const foundCountry = countries.find(c => 
          c.name.toLowerCase() === defaultAddr.country.toLowerCase() ||
          c.isoCode === defaultAddr.country
        )
        formData.value.country = foundCountry?.isoCode || ''
      }
    }
    
    // Llenar links
    if (profile.links && profile.links.length > 0) {
      formData.value.links = profile.links.map(link => ({
        id: link.id, // Include ID to update existing links
        url: link.url?.replace('https://', '').replace('http://', '') || '',
        title: link.title || '',
        order: link.order,
        is_active: link.is_active !== undefined ? link.is_active : true
      }))
    }
    
    // Load existing gallery photos
    if (profile.gallery_photos && profile.gallery_photos.length > 0) {
      existingPhotos.value = profile.gallery_photos
    }
  }
})

function handleFileSelect(event) {
  const files = Array.from(event.target.files)
  
  // Validate file types and sizes
  const validFiles = files.filter(file => {
    const isValidType = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'].includes(file.type)
    const isValidSize = file.size <= 800 * 1024 // 800KB
    return isValidType && isValidSize
  })
  
  if (validFiles.length > 0) {
    uploadedFiles.value.push(...validFiles)
  }
}

function handleFileDrop(event) {
  const files = Array.from(event.dataTransfer.files)
  
  // Validate file types and sizes
  const validFiles = files.filter(file => {
    const isValidType = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'].includes(file.type)
    const isValidSize = file.size <= 800 * 1024 // 800KB
    return isValidType && isValidSize
  })
  
  if (validFiles.length > 0) {
    uploadedFiles.value.push(...validFiles)
  }
}

function removeFile(index) {
  uploadedFiles.value.splice(index, 1)
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i)) + sizes[i]
}

function getImageUrl(imagePath) {
  // If it's already a full URL, return it
  if (imagePath.startsWith('http')) {
    return imagePath
  }
  // Otherwise, prepend the API base URL
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  // Remove /api from base URL if exists for media files
  const mediaBaseUrl = baseUrl.replace('/api', '')
  return `${mediaBaseUrl}${imagePath}`
}

function removeExistingPhoto(photoId) {
  // Add to photos to delete list
  photosToDelete.value.push(photoId)
  // Remove from existing photos display
  existingPhotos.value = existingPhotos.value.filter(photo => photo.id !== photoId)
}

function addLink() {
  formData.value.links.push({ url: '', title: '' })
}

function removeLink(index) {
  formData.value.links.splice(index, 1)
}

function onCountryChange() {
  // Reset state when country changes
  formData.value.state = ''
}

async function handleSubmit() {
  isLoading.value = true
  
  try {
    // Get country name from isoCode
    const selectedCountry = countries.find(c => c.isoCode === formData.value.country)
    const countryName = selectedCountry ? selectedCountry.name : formData.value.country
    
    // Prepare basic profile data
    const basicInfo = {
      first_name: formData.value.first_name,
      last_name: formData.value.last_name,
      email: formData.value.email,
      phone: formData.value.phone,
      username: formData.value.username,
      about: formData.value.about,
      note: formData.value.note,
      current_status: formData.value.current_status
    }
    
    // Prepare address data (if default address exists, update it, otherwise create new)
    const addresses = []
    if (formData.value.address_line1 && formData.value.city && formData.value.state && countryName) {
      const addressData = {
        country: countryName,
        state: formData.value.state,
        city: formData.value.city,
        address_line_1: formData.value.address_line1
      }
      
      // Add zip_code if it has a value (required for new addresses)
      if (formData.value.postal_code) {
        addressData.zip_code = formData.value.postal_code
      } else if (!profileStore.defaultAddress?.id) {
        // If creating new address, zip_code is required
        addressData.zip_code = ''
      }
      
      // Add optional fields only if they have values
      if (formData.value.address_line2) {
        addressData.address_line_2 = formData.value.address_line2
      }
      
      if (formData.value.additional_details) {
        addressData.additional_details = formData.value.additional_details
      }
      
      // Set as default
      addressData.is_default_shipping = true
      addressData.is_default_billing = true
      
      // If there's a default address, add its ID to update it
      if (profileStore.defaultAddress?.id) {
        addressData.id = profileStore.defaultAddress.id
      }
      
      addresses.push(addressData)
    }
    
    // Prepare links data
    const links = formData.value.links
      .filter(link => link.url && link.title) // Only include filled links
      .map((link, index) => {
        const linkData = {
          title: link.title,
          url: link.url.startsWith('http') ? link.url : `https://${link.url}`,
          order: index + 1,
          is_active: link.is_active !== undefined ? link.is_active : true
        }
        
        // If link has ID, include it to update existing link
        if (link.id) {
          linkData.id = link.id
        }
        
        return linkData
      })
    
    // Check if we have images to upload
    if (uploadedFiles.value.length > 0) {
      // Upload images using multipart/form-data
      const imageMeta = uploadedFiles.value.map((file, index) => ({
        caption: file.name,
        is_profile_picture: index === 0 && existingPhotos.value.length === 0 // First image is profile picture only if no existing photos
      }))
      
      const result = await profileStore.uploadGalleryImages({
        images: uploadedFiles.value,
        basicInfo: basicInfo,
        imageMeta: imageMeta
      })
      
      if (result.success) {
        // Clear uploaded files
        uploadedFiles.value = []
        
        // Reset file input to allow selecting same files again
        fileInputKey.value++
        
        // Update existing photos with new data from server
        if (result.data && result.data.gallery_photos) {
          existingPhotos.value = result.data.gallery_photos
        } else {
          // If no gallery_photos in response, reload profile
          await profileStore.fetchProfile()
          if (profileStore.profile && profileStore.profile.gallery_photos) {
            existingPhotos.value = profileStore.profile.gallery_photos
          }
        }
        
        // Clear deleted photos list
        photosToDelete.value = []
        
        // TODO: Mostrar notificación de éxito
      } else {
        console.error('Error al actualizar perfil:', result.error)
        // TODO: Mostrar notificación de error
      }
    } else {
      // Prepare gallery_photos (keep existing photos not marked for deletion)
      const gallery_photos = existingPhotos.value
        .filter(photo => !photosToDelete.value.includes(photo.id))
        .map(photo => ({
          id: photo.id
          // Only include ID to keep the photo, metadata updates would be here
        }))
      
      // Update complete profile with nested data (no new images to upload)
      const dataToSend = {
        basicInfo: basicInfo,
        addresses: addresses.length > 0 ? addresses : undefined,
        links: links.length > 0 ? links : undefined,
        gallery_photos: gallery_photos.length > 0 ? gallery_photos : undefined
      }
      
      const result = await profileStore.updateProfileComplete(dataToSend)
      
      if (result.success) {
        // Update existing photos with new data from server
        if (result.data.gallery_photos) {
          existingPhotos.value = result.data.gallery_photos
        }
        
        // Clear deleted photos list
        photosToDelete.value = []
        
        // TODO: Mostrar notificación de éxito
      } else {
        console.error('Error al actualizar perfil:', result.error)
        // TODO: Mostrar notificación de error
      }
    }
  } catch (error) {
    console.error('Error:', error)
    // TODO: Mostrar notificación de error
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.font-comfortaa {
  font-family: 'Comfortaa', cursive;
}
</style>

