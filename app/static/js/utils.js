/**
 * Display a temporary contextual message in a designated message box.
 *
 * This function shows a message (info, success, or error) in the element
 * with the ID `message-box`, applying Tailwind CSS styles accordingly.
 *
 */
 function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

 /* @param {string} message - The message text to display.
 * @param {'success' | 'error' | 'info'} [type='info'] - The type of message.
 */

function showMessage(message, type = 'info') {
  const messageBox = document.getElementById('message-box');

  // Ensure the message box exists in the DOM
  if (!messageBox) {
    console.warn('No element with ID "message-box" found in the DOM.');
    return;
  }

  // Reset base styles
  messageBox.className = 'p-3 mb-4 rounded text-sm';

  // Apply type-specific Tailwind classes
  switch (type) {
    case 'success':
      messageBox.classList.add('bg-green-100', 'text-green-700');
      break;
    case 'error':
      messageBox.classList.add('bg-red-100', 'text-red-700');
      break;
    default:
      messageBox.classList.add('bg-blue-100', 'text-blue-700');
  }

  // Display the message
  messageBox.textContent = message;
  messageBox.classList.remove('hidden');

  // Auto-hide after 4 seconds
  setTimeout(() => {
    messageBox.classList.add('hidden');
  }, 4000);
}
