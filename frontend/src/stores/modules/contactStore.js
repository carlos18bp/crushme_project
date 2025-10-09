/**
 * Contact Store - CrushMe
 * Manages contact form submissions
 */
import { defineStore } from 'pinia';
import { create_request } from '@/services/request_http.js';

export const useContactStore = defineStore('contact', {
  state: () => ({
    isSubmitting: false,
    lastSubmittedContact: null,
    error: null,
    successMessage: null
  }),

  actions: {
    /**
     * Send contact form
     * @param {Object} contactData - Contact form data
     * @param {string} contactData.email - Email address
     * @param {string} contactData.nombre - Full name
     * @param {string} contactData.numero - Phone number (optional)
     * @param {string} contactData.asunto - Subject
     * @param {string} contactData.texto - Message text
     * @returns {Promise<Object>} - Response from API
     */
    async sendContactForm(contactData) {
      this.isSubmitting = true;
      this.error = null;
      this.successMessage = null;

      try {
        const response = await create_request('contact/', contactData);

        if (response.data.success) {
          this.lastSubmittedContact = response.data.contact;
          this.successMessage = response.data.message;
          return {
            success: true,
            message: response.data.message,
            contact: response.data.contact
          };
        } else {
          throw new Error('Unexpected response format');
        }
      } catch (error) {
        
        // Handle 404 - Backend not available
        if (error.response?.status === 404) {
          this.error = {
            general: 'El servidor no está disponible. Por favor verifica que el backend esté corriendo en http://localhost:8000'
          };
          return {
            success: false,
            errors: this.error
          };
        }
        
        // Handle validation errors
        if (error.response?.data?.errors) {
          this.error = error.response.data.errors;
          return {
            success: false,
            errors: error.response.data.errors
          };
        }
        
        // Handle network errors
        if (!error.response) {
          this.error = {
            general: 'Error de conexión. Por favor verifica tu conexión a internet y que el backend esté corriendo.'
          };
          return {
            success: false,
            errors: this.error
          };
        }
        
        // Handle general errors
        this.error = {
          general: error.response?.data?.message || error.message || 'Error al enviar el mensaje'
        };
        
        return {
          success: false,
          errors: this.error
        };
      } finally {
        this.isSubmitting = false;
      }
    },

    /**
     * Clear form state
     */
    clearState() {
      this.error = null;
      this.successMessage = null;
      this.lastSubmittedContact = null;
    },

    /**
     * Reset store to initial state
     */
    reset() {
      this.isSubmitting = false;
      this.lastSubmittedContact = null;
      this.error = null;
      this.successMessage = null;
    }
  },

  getters: {
    /**
     * Check if there are any errors
     */
    hasErrors: (state) => {
      return state.error !== null && Object.keys(state.error).length > 0;
    },

    /**
     * Get formatted error messages
     */
    errorMessages: (state) => {
      if (!state.error) return [];
      
      const messages = [];
      for (const [field, errors] of Object.entries(state.error)) {
        if (Array.isArray(errors)) {
          messages.push(...errors);
        } else {
          messages.push(errors);
        }
      }
      return messages;
    }
  }
});

