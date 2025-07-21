// analytics/errors.js

import client from '../axios_client.js';

window.addEventListener('error', (e) => {
  const sessionId = localStorage.getItem('session_id');

  const errorPayload = {
    session_id: sessionId,
    error_message: e.message,
    url: e.filename || window.location.href,
    stack_trace: e.error && e.error.stack ? e.error.stack : '',
    error_type: 'js-runtime'
  };

  client.post('/analytics/error', errorPayload).catch((err) => {
    console.warn('Failed to log frontend error:', err);
  });
});
