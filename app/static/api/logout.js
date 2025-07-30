function initLogoutButtons() {
  const logoutButtons = document.querySelectorAll('.logout-btn');

  if (logoutButtons.length === 0) {
    console.warn("No logout buttons found.");
    return;
  }

  logoutButtons.forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault(); // prevent default anchor behavior
      btn.disabled = true;
      btn.textContent = 'Logging out...';

      try {
        const res = await fetch('/api/v1/auth/logout', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' }
        });

        if (res.ok) {
          window.location.href = '/dcp/auth/login';
        } else {
          const data = await res.json();
          alert("Logout failed: " + (data.msg || res.statusText));
        }
      } catch (err) {
        console.error("Logout error:", err);
        alert("Unexpected error during logout.");
      } finally {
        btn.disabled = false;
        btn.textContent = 'Logout';
      }
    });
  });
}

// Run after DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initLogoutButtons);
} else {
  initLogoutButtons();
}
