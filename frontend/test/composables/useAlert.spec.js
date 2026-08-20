import Swal from 'sweetalert2';

import { useAlert } from '@/composables/useAlert';

jest.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (key) => `translated:${key}` }),
}));

jest.mock('sweetalert2', () => ({
  fire: jest.fn(),
  close: jest.fn(),
  mixin: jest.fn(),
  stopTimer: jest.fn(),
  resumeTimer: jest.fn(),
}));

describe('useAlert', () => {
  test('shows a localized success alert with the provided message', () => {
    const { showSuccess } = useAlert();

    showSuccess('Order saved');

    expect(Swal.fire).toHaveBeenCalledWith(expect.objectContaining({
      icon: 'success',
      title: 'translated:alerts.success.title',
      text: 'Order saved',
      confirmButtonText: 'translated:alerts.success.confirmButton',
    }));
  });

  test('allows callers to override default confirmation options', () => {
    const { showConfirm } = useAlert();

    showConfirm('Delete item?', 'Confirm deletion', { confirmButtonColor: '#000' });

    expect(Swal.fire).toHaveBeenCalledWith(expect.objectContaining({
      icon: 'question',
      title: 'Confirm deletion',
      text: 'Delete item?',
      showCancelButton: true,
      confirmButtonColor: '#000',
    }));
  });

  test('closes the active alert', () => {
    const { closeAlert } = useAlert();

    closeAlert();

    expect(Swal.close).toHaveBeenCalledTimes(1);
  });
});
