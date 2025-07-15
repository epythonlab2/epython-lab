document.getElementById('logout-btn').addEventListener('click', async () => {
  try {
    const res = await fetch('/api/v1/auth/logout', {
      method: 'POST',
      credentials: 'include',  // important to send cookies
      headers: { 'Content-Type': 'application/json' }
    });

    if (res.ok) {
      // Redirect to login page after logout
      window.location.href = '/dcp/auth/login';
    } else {
      const data = await res.json();
      alert("Logout failed: " + (data.msg || res.statusText));
    }
  } catch (err) {
    console.error("Logout error:", err);
  }
});
