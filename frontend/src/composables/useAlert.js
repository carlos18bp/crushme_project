/**
 * SweetAlert2 Composable - CrushMe
 * Provides reusable alert functions with custom styling and i18n support
 */
import Swal from 'sweetalert2';
import { useI18n } from 'vue-i18n';

export function useAlert() {
  const { t } = useI18n();

  /**
   * Show success alert
   * @param {string} message - Success message
   * @param {string} title - Alert title (optional, uses i18n if not provided)
   * @param {Object} options - Additional SweetAlert2 options
   */
  const showSuccess = (message, title = null, options = {}) => {
    return Swal.fire({
      icon: 'success',
      title: title || t('alerts.success.title'),
      text: message,
      confirmButtonText: t('alerts.success.confirmButton'),
      confirmButtonColor: '#406582', // brand-blue-medium
      timer: 5000,
      timerProgressBar: true,
      customClass: {
        popup: 'font-poppins',
        title: 'font-comfortaa',
        confirmButton: 'font-poppins'
      },
      ...options
    });
  };

  /**
   * Show error alert
   * @param {string} message - Error message
   * @param {string} title - Alert title (optional, uses i18n if not provided)
   * @param {Object} options - Additional SweetAlert2 options
   */
  const showError = (message, title = null, options = {}) => {
    return Swal.fire({
      icon: 'error',
      title: title || t('alerts.error.title'),
      text: message,
      confirmButtonText: t('alerts.error.confirmButton'),
      confirmButtonColor: '#BF5E81', // brand-pink-dark
      customClass: {
        popup: 'font-poppins',
        title: 'font-comfortaa',
        confirmButton: 'font-poppins'
      },
      ...options
    });
  };

  /**
   * Show warning alert
   * @param {string} message - Warning message
   * @param {string} title - Alert title (optional, uses i18n if not provided)
   * @param {Object} options - Additional SweetAlert2 options
   */
  const showWarning = (message, title = null, options = {}) => {
    return Swal.fire({
      icon: 'warning',
      title: title || t('alerts.warning.title'),
      text: message,
      confirmButtonText: t('alerts.warning.confirmButton'),
      confirmButtonColor: '#DA9DFF', // brand-purple-light
      customClass: {
        popup: 'font-poppins',
        title: 'font-comfortaa',
        confirmButton: 'font-poppins'
      },
      ...options
    });
  };

  /**
   * Show info alert
   * @param {string} message - Info message
   * @param {string} title - Alert title (optional, uses i18n if not provided)
   * @param {Object} options - Additional SweetAlert2 options
   */
  const showInfo = (message, title = null, options = {}) => {
    return Swal.fire({
      icon: 'info',
      title: title || t('alerts.info.title'),
      text: message,
      confirmButtonText: t('alerts.info.confirmButton'),
      confirmButtonColor: '#A4C1D0', // brand-blue-light
      customClass: {
        popup: 'font-poppins',
        title: 'font-comfortaa',
        confirmButton: 'font-poppins'
      },
      ...options
    });
  };

  /**
   * Show confirmation dialog
   * @param {string} message - Confirmation message
   * @param {string} title - Alert title (optional, uses i18n if not provided)
   * @param {Object} options - Additional SweetAlert2 options
   */
  const showConfirm = (message, title = null, options = {}) => {
    return Swal.fire({
      icon: 'question',
      title: title || t('alerts.confirm.title'),
      text: message,
      showCancelButton: true,
      confirmButtonText: t('alerts.confirm.confirmButton'),
      cancelButtonText: t('alerts.confirm.cancelButton'),
      confirmButtonColor: '#406582', // brand-blue-medium
      cancelButtonColor: '#BF5E81', // brand-pink-dark
      customClass: {
        popup: 'font-poppins',
        title: 'font-comfortaa',
        confirmButton: 'font-poppins',
        cancelButton: 'font-poppins'
      },
      ...options
    });
  };

  /**
   * Show loading alert
   * @param {string} message - Loading message (optional, uses i18n if not provided)
   * @param {string} title - Alert title (optional)
   */
  const showLoading = (message = null, title = '') => {
    return Swal.fire({
      title: title || t('alerts.loading.title'),
      text: message || t('alerts.loading.message'),
      allowOutsideClick: false,
      allowEscapeKey: false,
      showConfirmButton: false,
      customClass: {
        popup: 'font-poppins',
        title: 'font-comfortaa'
      },
      didOpen: () => {
        Swal.showLoading();
      }
    });
  };

  /**
   * Close current alert
   */
  const closeAlert = () => {
    Swal.close();
  };

  /**
   * Show toast notification (small notification in corner)
   * @param {string} message - Toast message
   * @param {string} icon - Icon type (success, error, warning, info)
   * @param {Object} options - Additional SweetAlert2 options
   */
  const showToast = (message, icon = 'success', options = {}) => {
    const Toast = Swal.mixin({
      toast: true,
      position: 'top-end',
      showConfirmButton: false,
      timer: 3000,
      timerProgressBar: true,
      customClass: {
        popup: 'font-poppins'
      },
      didOpen: (toast) => {
        toast.addEventListener('mouseenter', Swal.stopTimer);
        toast.addEventListener('mouseleave', Swal.resumeTimer);
      }
    });

    return Toast.fire({
      icon: icon,
      title: message,
      ...options
    });
  };

  return {
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showConfirm,
    showLoading,
    showToast,
    closeAlert
  };
}

