/**
 * Displays a temporary message to the user with contextual styling.
 * 
 * Automatically injects the message box into the DOM if not found.
 * Uses Tailwind CSS for styling.
 * 
 * @param {string} message - The message text to display.
 * @param {'success' | 'error' | 'info'} [type='info'] - The type of message.
 */
function showMessage(message, type = 'info') {
    const boxId = 'message-box';
    let messageBox = document.getElementById(boxId);
  
    // Create message box if it does not exist
    if (!messageBox) {
      messageBox = document.createElement('div');
      messageBox.id = boxId;
      messageBox.className = 'hidden p-3 mb-4 rounded text-sm';
      messageBox.setAttribute('aria-live', 'polite');
      document.body.appendChild(messageBox);
    }
  
    // Reset any existing styles
    messageBox.className = 'p-3 mb-4 rounded text-sm';
  
    // Apply contextual styles
    switch (type) {
      case 'error':
        messageBox.classList.add('bg-red-100', 'text-red-700');
        break;
      case 'success':
        messageBox.classList.add('bg-green-100', 'text-green-700');
        break;
      default:
        messageBox.classList.add('bg-blue-100', 'text-blue-700');
    }
  
    // Set message content and show the box
    messageBox.textContent = message;
    messageBox.classList.remove('hidden');
  
    // Automatically hide the message after 4 seconds
    setTimeout(() => {
      messageBox.classList.add('hidden');
    }, 5000);
  }
  
  // Optional: export for modular use
  // export { showMessage };
  