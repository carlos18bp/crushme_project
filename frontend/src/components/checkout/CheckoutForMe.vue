<template>
  <div class="checkout-form-section">
    <!-- Full Name -->
    <div class="form-group">
      <label for="fullname">Full name <span class="text-red-500">*</span></label>
      <input
        type="text"
        id="fullname"
        v-model="form.fullName"
        placeholder="John Doe"
        class="form-input"
        required
      >
    </div>

    <!-- Country -->
    <div class="form-group">
      <label for="country">Country</label>
      <select
        id="country"
        v-model="form.country"
        class="form-input form-select"
        disabled
      >
        <option value="CO">🇨🇴 Colombia</option>
      </select>
    </div>

    <!-- Address Line 1 -->
    <div class="form-group">
      <label for="address1">Address line 1 <span class="text-red-500">*</span></label>
      <input
        type="text"
        id="address1"
        v-model="form.address1"
        placeholder="123 Main Street"
        class="form-input"
        required
      >
    </div>

    <!-- Address Line 2 -->
    <div class="form-group">
      <label for="address2">Address line 2</label>
      <input
        type="text"
        id="address2"
        v-model="form.address2"
        placeholder="Apt, suite, unit number, etc. (optional)"
        class="form-input"
      >
    </div>

    <!-- City -->
    <div class="form-group">
      <label for="city">Ciudad <span class="text-red-500">*</span></label>
      <input
        type="text"
        id="city"
        v-model="form.city"
        placeholder="Ej: Bogotá, Medellín, Cali..."
        class="form-input"
        required
        list="colombia-cities"
        @input="$emit('city-change', form.city)"
      >
      <datalist id="colombia-cities">
        <option value="Medellín"></option>
        <option value="Bogotá"></option>
        <option value="Cali"></option>
        <option value="Barranquilla"></option>
        <option value="Cartagena"></option>
        <option value="Santa Marta"></option>
        <option value="San Andrés Isla"></option>
        <option value="Providencia"></option>
        <option value="Santa Catalina"></option>
        <option value="Bucaramanga"></option>
        <option value="Pereira"></option>
        <option value="Manizales"></option>
        <option value="Ibagué"></option>
        <option value="Villavicencio"></option>
        <option value="Pasto"></option>
        <option value="Neiva"></option>
      </datalist>
      <p class="city-shipping-info" v-if="form.city && shippingCost">
        <span>
          📦 Costo de envío: {{ formatCOP(shippingCost) }}
        </span>
      </p>
    </div>

    <!-- State/Department -->
    <div class="form-row">
      <div class="form-group">
        <label for="state">Departamento <span class="text-red-500">*</span></label>
        <select
          id="state"
          v-model="form.state"
          class="form-input form-select"
          required
        >
          <option value="">Selecciona un departamento</option>
          <option v-for="state in availableStates" :key="state.isoCode" :value="state.name">
            {{ state.name }}
          </option>
        </select>
      </div>

      <!-- ZIP Code -->
      <div class="form-group">
        <label for="zipCode">ZIP / Postal code <span class="text-red-500">*</span></label>
        <input
          type="text"
          id="zipCode"
          v-model="form.zipCode"
          placeholder="110111"
          class="form-input"
          required
        >
      </div>
    </div>

    <!-- Phone -->
    <div class="form-group">
      <label for="phone">Phone number <span class="text-red-500">*</span></label>
      <div class="phone-input-group">
        <select v-model="form.phoneCode" class="phone-code-select">
          <option v-for="country in countryCodes" :key="country.code" :value="country.code">
            {{ country.flag }} {{ country.code }}
          </option>
        </select>
        <input
          type="tel"
          id="phone"
          v-model="form.phone"
          placeholder="3001234567"
          class="form-input phone-input"
          required
        >
      </div>
    </div>

    <!-- Additional Details -->
    <div class="form-group">
      <label for="additionalDetails">{{ $t('cart.checkout.form.additionalDetails') }}</label>
      <textarea
        id="additionalDetails"
        v-model="form.additionalDetails"
        :placeholder="$t('cart.checkout.form.placeholders.additionalDetails')"
        class="form-input form-textarea"
        rows="3"
      ></textarea>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { State } from 'country-state-city';
import { formatCOP } from '@/utils/priceHelper.js';

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  shippingCost: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['update:modelValue', 'city-change']);

const form = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

// Available states for Colombia
const availableStates = computed(() => {
  return State.getStatesOfCountry('CO');
});

// Country codes for phone selector
const countryCodes = [
  { code: '+57', flag: '🇨🇴', name: 'Colombia' }
];
</script>

<style scoped>
.checkout-form-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-input {
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #ec4899;
  box-shadow: 0 0 0 3px rgba(236, 72, 153, 0.1);
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.phone-input-group {
  display: flex;
  gap: 0.5rem;
}

.phone-code-select {
  width: 120px;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 1rem;
}

.phone-input {
  flex: 1;
}

.city-shipping-info {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #be185d;
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
