import { createUser } from '/static/api/user_api.js';

export function initAddUserModal(reloadUsersCallback) {
  const modal = document.getElementById('add-user-modal');
  const openBtn = document.getElementById('open-add-user-modal');
  const cancelBtn = document.getElementById('cancel-add-user');
  const form = document.getElementById('add-user-form');

  if (!modal || !openBtn || !cancelBtn || !form) {
    console.warn('User modal elements not found.');
    return;
  }

  openBtn.addEventListener('click', () => {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  });

  cancelBtn.addEventListener('click', () => {
    hideModal();
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const userData = {
      username: formData.get('username')?.trim(),
      email: formData.get('email')?.trim(),
      password: formData.get('password'),
      role: formData.get('role')
    };

    if (!userData.username) {
      showToast('Username is required.', 'error');
      return;
    }

    if (!validateEmail(userData.email)) {
      showToast('Invalid email format.', 'error');
      return;
    }

    if (!userData.password || userData.password.length < 6) {
      showToast('Password must be at least 6 characters.', 'error');
      return;
    }

    try {
      await createUser(userData);
      showToast('✅ User created successfully', 'success');
      hideModal();
      reloadUsersCallback();
    } catch (err) {
      console.error('User creation failed:', err);
      const msg = err.response?.data?.msg ||
                  JSON.stringify(err.response?.data) ||
                  'Failed to create user.';
      showToast(`❌ ${msg}`, 'error');
    }
  });

  function hideModal() {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    form.reset();
  }

  function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function showToast(message, type = 'info') {
    const colors = {
      success: '#16a34a',  // green
      error: '#dc2626',    // red
      warning: '#f59e0b',  // yellow
      info: '#3b82f6'      // blue
    };

    Toastify({
      text: message,
      duration: 4000,
      gravity: 'top',
      position: 'right',
      backgroundColor: colors[type] || colors.info,
      close: true
    }).showToast();
  }
}
