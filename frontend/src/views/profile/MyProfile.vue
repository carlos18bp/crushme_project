<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">
    <form @submit.prevent="handleSubmit" class="space-y-8 md:space-y-10">
      
      <!-- Shipping info section -->
      <div>
        <h2 class="text-xl md:text-2xl font-semibold text-gray-900 mb-4 md:mb-6 font-comfortaa">
          {{ $t('profile.form.shippingDetails.title') }}
        </h2>

        <div class="space-y-4 md:space-y-6">
          <!-- First name & Last name -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
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
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
            <div>
              <label for="email" class="block text-xs md:text-sm font-medium text-gray-900 mb-2">
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
              <label for="phone" class="block text-xs md:text-sm font-medium text-gray-900 mb-2">
                {{ $t('profile.form.basicInfo.phone') }}
              </label>
              <input
                id="phone"
                v-model="formData.phone"
                type="tel"
                placeholder="3001234567"
                class="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors"
              />
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
              disabled
              class="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors bg-gray-100 cursor-not-allowed"
            >
              <option value="">{{ $t('profile.form.placeholders.selectCountry') }}</option>
              <option v-for="country in countries" :key="country.isoCode" :value="country.isoCode">
                {{ country.flag }} {{ country.name }}
              </option>
            </select>
          </div>

          <!-- State & ZIP code -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
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
        <h2 class="text-xl md:text-2xl font-semibold text-gray-900 mb-4 md:mb-6 font-comfortaa">
          {{ $t('profile.form.publicProfile.title') }}
        </h2>

        <div class="space-y-4 md:space-y-6">
          <!-- Crush Verification Badge -->
          <div v-if="profileStore.isCrushVerified" class="mb-4 md:mb-6">
            <div class="inline-flex items-center gap-2 px-3 py-1.5 md:px-4 md:py-2 bg-gradient-to-r from-brand-pink-dark to-pink-600 text-white rounded-full shadow-lg">
              <svg class="w-4 h-4 md:w-5 md:h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <span class="font-bold text-sm">{{ $t('profile.form.crush.verified') || 'CRUSH VERIFICADO' }}</span>
            </div>
          </div>

          <!-- Crush Verification Section -->
          <div v-if="!profileStore.isCrushVerified" class="bg-gradient-to-br from-pink-50 to-purple-50 rounded-xl md:rounded-2xl p-4 md:p-6 border border-pink-200">
            <!-- Pending Status -->
            <div v-if="profileStore.hasPendingCrushRequest" class="text-center">
              <div class="inline-flex items-center justify-center w-16 h-16 bg-yellow-100 rounded-full mb-4">
                <svg class="w-8 h-8 text-yellow-600 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold text-gray-900 mb-2 font-comfortaa">
                {{ $t('profile.form.crush.pendingTitle') || 'Solicitud Pendiente' }}
              </h3>
              <p class="text-sm text-gray-600 mb-4">
                {{ $t('profile.form.crush.pendingMessage') || 'Tu solicitud está siendo revisada por un administrador.' }}
              </p>
              <p v-if="profileStore.crushRequestedAt" class="text-xs text-gray-500 mb-4">
                {{ $t('profile.form.crush.requestedAt') || 'Solicitado el' }}: 
                {{ new Date(profileStore.crushRequestedAt).toLocaleDateString() }}
              </p>
              <button
                type="button"
                @click="handleCancelCrushRequest"
                :disabled="isLoading"
                class="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-full hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ $t('profile.form.crush.cancelRequest') || 'Cancelar Solicitud' }}
              </button>
            </div>

            <!-- Rejected Status -->
            <div v-else-if="profileStore.crushVerificationStatus === 'rejected'" class="text-center">
              <div class="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
                <svg class="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold text-gray-900 mb-2 font-comfortaa">
                {{ $t('profile.form.crush.rejectedTitle') || 'Solicitud Rechazada' }}
              </h3>
              <p class="text-sm text-gray-600 mb-4">
                {{ $t('profile.form.crush.rejectedMessage') || 'Tu solicitud fue revisada pero no fue aprobada.' }}
              </p>
              <div v-if="profileStore.crushRejectionReason" class="bg-white rounded-lg p-4 mb-4">
                <p class="text-xs text-gray-500 mb-1 font-semibold">
                  {{ $t('profile.form.crush.rejectionReason') || 'Motivo' }}:
                </p>
                <p class="text-sm text-gray-700">{{ profileStore.crushRejectionReason }}</p>
              </div>
              <p class="text-sm text-gray-600 mb-4">
                {{ $t('profile.form.crush.canReapply') || 'Puedes volver a solicitar verificación.' }}
              </p>
              <button
                type="button"
                @click="handleRequestCrushVerification"
                :disabled="isLoading"
                class="px-6 py-3 bg-gradient-to-r from-brand-pink-dark to-pink-600 text-white font-medium rounded-full hover:from-brand-pink-medium hover:to-pink-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md font-comfortaa"
              >
                <span v-if="isLoading">{{ $t('profile.form.buttons.loading') }}...</span>
                <span v-else>🌟 {{ $t('profile.form.crush.requestButton') || 'Solicitar de Nuevo' }}</span>
              </button>
            </div>

            <!-- Can Request -->
            <div v-else-if="profileStore.canRequestCrushVerification" class="text-center">
              <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-brand-pink-lighter to-purple-200 rounded-full mb-4">
                <svg class="w-8 h-8 text-brand-pink-dark" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold text-gray-900 mb-2 font-comfortaa">
                {{ $t('profile.form.crush.title') || 'Conviértete en Crush Verificado' }}
              </h3>
              <p class="text-sm text-gray-600 mb-4 max-w-md mx-auto">
                {{ $t('profile.form.crush.description') || 'Los Crushes verificados obtienen un badge especial y mayor visibilidad en la plataforma.' }}
              </p>
              <button
                type="button"
                @click="handleRequestCrushVerification"
                :disabled="isLoading"
                class="px-6 py-3 bg-gradient-to-r from-brand-pink-dark to-pink-600 text-white font-medium rounded-full hover:from-brand-pink-medium hover:to-pink-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md font-comfortaa"
              >
                <span v-if="isLoading">{{ $t('profile.form.buttons.loading') }}...</span>
                <span v-else>🌟 {{ $t('profile.form.crush.requestButton') || 'Solicitar Verificación' }}</span>
              </button>
            </div>
          </div>

          <!-- Profile & Cover Photos -->
          <div>
            <label class="block text-xs md:text-sm font-medium text-gray-900 mb-2 md:mb-3">
              {{ $t('profile.form.publicProfile.photos') || 'Fotos de perfil' }}
            </label>
            
            <!-- Cover Photo -->
            <div class="relative mb-20 md:mb-6">
              <div 
                @click="$refs.coverImageInput.click()"
                class="w-full h-32 md:h-40 lg:h-48 rounded-xl md:rounded-2xl border-2 border-dashed border-gray-300 flex items-center justify-center overflow-hidden hover:border-brand-pink-dark transition-colors cursor-pointer group relative"
                :class="{ 'bg-gradient-to-r from-brand-pink-lighter via-purple-200 to-blue-200': !coverImagePreview && !profileStore.coverImageUrl }"
              >
                <!-- Cover Image Preview or Existing -->
                <img 
                  v-if="coverImagePreview || profileStore.coverImageUrl"
                  :src="coverImagePreview || getImageUrlWithCacheBusting(profileStore.coverImageUrl)"
                  alt="Cover"
                  class="w-full h-full object-cover"
                />
                
                <!-- Placeholder -->
                <div v-else class="text-center">
                  <svg class="w-12 h-12 text-gray-400 mx-auto mb-2 group-hover:text-brand-pink-dark transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <p class="text-sm font-medium text-gray-600 group-hover:text-brand-pink-dark transition-colors">
                    {{ $t('profile.form.publicProfile.coverPhoto') || 'Foto de portada' }}
                  </p>
                  <p class="text-xs text-gray-400 mt-1">1500 x 500 px</p>
                </div>
                
                <!-- Delete button for existing cover -->
                <button
                  v-if="profileStore.coverImageUrl && !coverImagePreview"
                  type="button"
                  @click.stop="handleRemoveCoverImage"
                  class="absolute top-3 right-3 p-2 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors opacity-0 group-hover:opacity-100"
                >
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <!-- Hidden file input for cover image -->
              <input
                ref="coverImageInput"
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
                class="hidden"
                @change="handleCoverImageSelect"
              />
              
              <!-- Profile Picture - Overlapping cover -->
              <div class="absolute -bottom-14 md:-bottom-16 left-4 md:left-8">
                <div class="relative">
                  <div 
                    @click="$refs.profilePictureInput.click()"
                    class="w-24 h-24 md:w-28 md:h-28 lg:w-32 lg:h-32 rounded-full border-4 border-white shadow-lg flex items-center justify-center cursor-pointer hover:shadow-xl transition-shadow group relative overflow-hidden"
                    :class="{ 'bg-gradient-to-br from-brand-pink-lighter to-purple-200': !profilePicturePreview && !profileStore.profilePictureUrl }"
                  >
                    <!-- Profile Picture Preview or Existing -->
                    <img 
                      v-if="profilePicturePreview || profileStore.profilePictureUrl"
                      :src="profilePicturePreview || getImageUrlWithCacheBusting(profileStore.profilePictureUrl)"
                      alt="Profile"
                      class="w-full h-full object-cover"
                    />
                    
                    <!-- Placeholder -->
                    <div v-else class="text-center">
                      <svg class="w-10 h-10 text-gray-400 mx-auto group-hover:text-brand-pink-dark transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                  </div>
                  
                  <!-- Camera button -->
                  <div class="absolute bottom-0 right-0 md:bottom-1 md:right-1 w-7 h-7 md:w-8 md:h-8 bg-brand-pink-dark rounded-full flex items-center justify-center shadow-md hover:bg-brand-pink-medium transition-colors cursor-pointer">
                    <svg class="w-3.5 h-3.5 md:w-4 md:h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  
                  <!-- Delete button for existing profile picture -->
                  <button
                    v-if="profileStore.profilePictureUrl && !profilePicturePreview"
                    type="button"
                    @click.stop="handleRemoveProfilePicture"
                    class="absolute top-0 right-0 p-1.5 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors"
                  >
                    <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <!-- Hidden file input for profile picture -->
                <input
                  ref="profilePictureInput"
                  type="file"
                  accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
                  class="hidden"
                  @change="handleProfilePictureSelect"
                />
                
                <p class="text-xs text-gray-500 mt-2 ml-2">
                  {{ $t('profile.form.publicProfile.profilePhoto') || 'Foto de perfil' }}
                </p>
              </div>
            </div>
            
            <!-- Spacer for overlapping profile picture -->
            <div class="h-16 md:h-20"></div>
          </div>

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
              <h4 class="text-xs md:text-sm font-medium text-gray-700 mb-2 md:mb-3">{{ $t('profile.form.gallery.currentPhotos') }}</h4>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 md:gap-4">
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
              <h4 class="text-xs md:text-sm font-medium text-gray-700 mb-2 md:mb-3">{{ $t('profile.form.gallery.newPhotos') }}</h4>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
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

            <div v-for="(link, index) in formData.links" :key="index" class="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4 mb-3 md:mb-4">
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500 text-sm">
                  https://
                </div>
                <input
                  v-model="link.url"
                  @input="cleanLinkUrl(link)"
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

      <!-- Preferences section -->
      <div>
        <h2 class="text-xl md:text-2xl font-semibold text-gray-900 mb-4 md:mb-6 font-comfortaa">
          {{ $t('profile.form.preferences.title') }}
        </h2>

        <div class="space-y-4 md:space-y-6">
          <!-- Language Preference -->
          <div class="max-w-md">
            <label for="language" class="block text-sm font-medium text-gray-900 mb-2">
              {{ $t('profile.form.preferences.language') }}
            </label>
            <div class="relative">
              <select
                id="language"
                v-model="selectedLanguage"
                @change="handleLanguageChange"
                class="block w-full rounded-lg border border-gray-300 px-4 py-3 pr-10 text-gray-900 focus:border-brand-pink-dark focus:ring-2 focus:ring-brand-pink-dark/20 transition-colors appearance-none cursor-pointer"
              >
                <option value="en">🇬🇧 English</option>
                <option value="es">🇪🇸 Español</option>
              </select>
              <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
            <p class="mt-2 text-xs text-gray-500">
              {{ $t('profile.form.preferences.languageHelp') }}
            </p>
          </div>
        </div>
      </div>

      <!-- Submit button -->
      <div class="flex flex-col sm:flex-row gap-3 md:gap-4 items-stretch sm:items-center">
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full sm:w-auto px-6 md:px-8 py-2.5 md:py-3 bg-brand-pink-dark text-white font-medium text-sm md:text-base rounded-full hover:bg-brand-pink-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-comfortaa shadow-md"
        >
          {{ isLoading ? $t('profile.form.buttons.loading') : $t('profile.form.buttons.save') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProfileStore } from '@/stores/modules/profileStore'
import { useAuthStore } from '@/stores/modules/authStore'
import { useI18nStore } from '@/stores/modules/i18nStore'
import { useAlert } from '@/composables/useAlert'
import { Country, State } from 'country-state-city'

const router = useRouter()
const profileStore = useProfileStore()
const authStore = useAuthStore()
const i18nStore = useI18nStore()
const { showSuccess, showError, showConfirm } = useAlert()

// Language preference
const selectedLanguage = ref(i18nStore.locale)

const isLoading = ref(false)
const uploadedFiles = ref([])
const existingPhotos = ref([])
const photosToDelete = ref([])
const fileInputKey = ref(0)

// Profile and cover images
const profilePictureFile = ref(null)
const coverImageFile = ref(null)
const profilePicturePreview = ref(null)
const coverImagePreview = ref(null)

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
  phoneCode: '+57',
  country: 'CO', // ⭐ Colombia por defecto
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
        formData.value.country = foundCountry?.isoCode || 'CO' // ⭐ Colombia por defecto
      }
    } else {
      // ⭐ Si no hay dirección, asegurar que Colombia esté seleccionada
      formData.value.country = 'CO'
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

function cleanLinkUrl(link) {
  // Remove https:// or http:// if user pastes a full URL
  if (link.url) {
    link.url = link.url.replace(/^https?:\/\//i, '')
  }
}

function onCountryChange() {
  // Reset state when country changes
  formData.value.state = ''
}

// ============================================
// PROFILE & COVER IMAGE HANDLERS
// ============================================

function handleProfilePictureSelect(event) {
  const file = event.target.files[0]
  
  if (!file) return
  
  // Validate the file
  const validation = profileStore.validateImageFile(file)
  
  if (!validation.valid) {
    showError(validation.errors.join('\n'), 'Archivo no válido')
    return
  }
  
  // Store file and create preview
  profilePictureFile.value = file
  profilePicturePreview.value = URL.createObjectURL(file)
}

function handleCoverImageSelect(event) {
  const file = event.target.files[0]
  
  if (!file) return
  
  // Validate the file
  const validation = profileStore.validateImageFile(file)
  
  if (!validation.valid) {
    showError(validation.errors.join('\n'), 'Archivo no válido')
    return
  }
  
  // Store file and create preview
  coverImageFile.value = file
  coverImagePreview.value = URL.createObjectURL(file)
}

async function handleRemoveProfilePicture() {
  const confirm = await showConfirm('¿Estás seguro de que quieres eliminar tu foto de perfil?')
  
  if (!confirm.isConfirmed) {
    return
  }
  
  const result = await profileStore.removeProfilePicture()
  
  if (result.success) {
    profilePictureFile.value = null
    profilePicturePreview.value = null
    showSuccess(result.message)
  } else {
    showError(result.error, 'Error')
  }
}

async function handleRemoveCoverImage() {
  const confirm = await showConfirm('¿Estás seguro de que quieres eliminar tu foto de portada?')
  
  if (!confirm.isConfirmed) {
    return
  }
  
  const result = await profileStore.removeCoverImage()
  
  if (result.success) {
    coverImageFile.value = null
    coverImagePreview.value = null
    showSuccess(result.message)
  } else {
    showError(result.error, 'Error')
  }
}

function getImageUrlWithCacheBusting(url) {
  return profileStore.getImageUrlWithCacheBusting(url)
}

// ============================================
// LANGUAGE PREFERENCE HANDLER
// ============================================

function handleLanguageChange() {
  const currentRoute = router.currentRoute.value.name
  const newLocale = selectedLanguage.value
  
  // Update the i18n store
  i18nStore.setLocale(newLocale)
  
  // Navigate to the same route but with new locale
  const routeBaseName = currentRoute.replace(/-en$|-es$/, '')
  router.push({ name: `${routeBaseName}-${newLocale}` })
  
  showSuccess(
    newLocale === 'en' 
      ? 'Language changed to English' 
      : 'Idioma cambiado a Español',
    '✓'
  )
}

// ============================================
// CRUSH VERIFICATION HANDLERS
// ============================================

async function handleRequestCrushVerification() {
  const confirm = await showConfirm(
    '¿Estás seguro de que quieres solicitar verificación como Crush?',
    'Solicitar Verificación'
  )
  
  if (!confirm.isConfirmed) {
    return
  }
  
  const result = await profileStore.requestCrushVerification()
  
  if (result.success) {
    showSuccess(result.message, '¡Solicitud Enviada!')
    // Reload profile to get updated status
    await profileStore.fetchProfile()
  } else {
    showError(result.error, 'Error al Solicitar')
  }
}

async function handleCancelCrushRequest() {
  const confirm = await showConfirm(
    '¿Estás seguro de que quieres cancelar tu solicitud de verificación?',
    'Cancelar Solicitud'
  )
  
  if (!confirm.isConfirmed) {
    return
  }
  
  const result = await profileStore.cancelCrushRequest()
  
  if (result.success) {
    showSuccess(result.message, 'Solicitud Cancelada')
    // Reload profile to get updated status
    await profileStore.fetchProfile()
  } else {
    showError(result.error, 'Error al Cancelar')
  }
}

async function handleSubmit() {
  isLoading.value = true
  
  try {
    // ============================================
    // STEP 1: Enviar información de texto primero
    // ============================================
    console.log('📝 [UPLOAD] Paso 1: Enviando información de texto...')
    
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
    
    // Prepare address data
    const addresses = []
    if (formData.value.address_line1 && formData.value.city && formData.value.state && countryName) {
      const addressData = {
        country: countryName,
        state: formData.value.state,
        city: formData.value.city,
        address_line_1: formData.value.address_line1
      }
      
      if (formData.value.postal_code) {
        addressData.zip_code = formData.value.postal_code
      } else if (!profileStore.defaultAddress?.id) {
        addressData.zip_code = ''
      }
      
      if (formData.value.address_line2) {
        addressData.address_line_2 = formData.value.address_line2
      }
      
      if (formData.value.additional_details) {
        addressData.additional_details = formData.value.additional_details
      }
      
      addressData.is_default_shipping = true
      addressData.is_default_billing = true
      
      if (profileStore.defaultAddress?.id) {
        addressData.id = profileStore.defaultAddress.id
      }
      
      addresses.push(addressData)
    }
    
    // Prepare links data
    const links = formData.value.links
      .filter(link => link.url && link.title)
      .map((link, index) => {
        const linkData = {
          title: link.title,
          url: link.url.startsWith('http') ? link.url : `https://${link.url}`,
          order: index + 1,
          is_active: link.is_active !== undefined ? link.is_active : true
        }
        
        if (link.id) {
          linkData.id = link.id
        }
        
        return linkData
      })
    
    // Prepare gallery_photos (keep existing photos not marked for deletion)
    const gallery_photos = existingPhotos.value
      .filter(photo => !photosToDelete.value.includes(photo.id))
      .map(photo => ({
        id: photo.id
      }))
    
    // Enviar información de texto primero
    const dataToSend = {
      basicInfo: basicInfo,
      addresses: addresses.length > 0 ? addresses : undefined,
      links: links.length > 0 ? links : undefined,
      gallery_photos: gallery_photos.length > 0 ? gallery_photos : undefined
    }
    
    const textResult = await profileStore.updateProfileComplete(dataToSend)
    
    if (!textResult.success) {
      showError(textResult.error, 'Error al actualizar información')
      return
    }
    
    console.log('✅ [UPLOAD] Información de texto enviada correctamente')
    
    // ============================================
    // STEP 2: Subir imagen de cover (si existe)
    // ============================================
    if (coverImageFile.value) {
      console.log('🖼️ [UPLOAD] Paso 2: Subiendo imagen de cover...')
      
      const coverResult = await profileStore.uploadProfileImages({
        coverImage: coverImageFile.value
      })
      
      if (coverResult.success) {
        coverImageFile.value = null
        if (coverImagePreview.value) {
          URL.revokeObjectURL(coverImagePreview.value)
          coverImagePreview.value = null
        }
        console.log('✅ [UPLOAD] Imagen de cover subida correctamente')
      } else {
        console.error('❌ [UPLOAD] Error al subir imagen de cover:', coverResult.error)
      }
    }
    
    // ============================================
    // STEP 3: Subir imagen de perfil (si existe)
    // ============================================
    if (profilePictureFile.value) {
      console.log('👤 [UPLOAD] Paso 3: Subiendo imagen de perfil...')
      
      const profileResult = await profileStore.uploadProfileImages({
        profilePicture: profilePictureFile.value
      })
      
      if (profileResult.success) {
        profilePictureFile.value = null
        if (profilePicturePreview.value) {
          URL.revokeObjectURL(profilePicturePreview.value)
          profilePicturePreview.value = null
        }
        console.log('✅ [UPLOAD] Imagen de perfil subida correctamente')
      } else {
        console.error('❌ [UPLOAD] Error al subir imagen de perfil:', profileResult.error)
      }
    }
    
    // ============================================
    // STEP 4: Subir imágenes de galería una por una (si existen)
    // ============================================
    if (uploadedFiles.value.length > 0) {
      console.log(`🖼️ [UPLOAD] Paso 4: Subiendo ${uploadedFiles.value.length} imágenes de galería...`)
      
      for (let i = 0; i < uploadedFiles.value.length; i++) {
        const file = uploadedFiles.value[i]
        console.log(`📷 [UPLOAD] Subiendo imagen ${i + 1}/${uploadedFiles.value.length}: ${file.name}`)
        
        const imageMeta = [{
          caption: file.name,
          is_profile_picture: i === 0 && existingPhotos.value.length === 0
        }]
        
        const result = await profileStore.uploadGalleryImages({
          images: [file], // Subir una imagen a la vez
          basicInfo: basicInfo,
          imageMeta: imageMeta
        })
        
        if (result.success) {
          console.log(`✅ [UPLOAD] Imagen ${i + 1}/${uploadedFiles.value.length} subida correctamente`)
          
          // Update existing photos with new data from server
          if (result.data && result.data.gallery_photos) {
            existingPhotos.value = result.data.gallery_photos
          }
        } else {
          console.error(`❌ [UPLOAD] Error al subir imagen ${i + 1}/${uploadedFiles.value.length}:`, result.error)
        }
      }
      
      // Clear uploaded files after all uploads
      uploadedFiles.value = []
      fileInputKey.value++
      console.log('✅ [UPLOAD] Todas las imágenes de galería subidas')
    }
    
    // Clear deleted photos list
    photosToDelete.value = []
    
    // Reload profile to get updated data
    await profileStore.fetchProfile()
    if (profileStore.profile && profileStore.profile.gallery_photos) {
      existingPhotos.value = profileStore.profile.gallery_photos
    }
    
    showSuccess('Perfil actualizado correctamente', '¡Éxito!')
  } catch (error) {
    console.error('Error:', error)
    showError('Ocurrió un error inesperado', 'Error')
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

