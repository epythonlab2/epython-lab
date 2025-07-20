// analytics/session.js

import client from '../axios_client.js';

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

export function trackSessionStart() {
  let sessionId = localStorage.getItem('session_id');
  if (!sessionId) {
    sessionId = generateUUID();
    localStorage.setItem('session_id', sessionId);
  }

  const deviceType = /Mobi|Android/i.test(navigator.userAgent) ? 'mobile' : 'desktop';

  client.post('/analytics/session/start', {
    session_id: sessionId,
    device_type: deviceType,
    country: ''  // Reserved for future use or geo IP injection from backend
  }).catch(err => {
    console.warn('Failed to start session:', err);
  });
}

export function trackSessionEnd(timeSpent = 0) {
  const sessionId = localStorage.getItem('session_id');
  if (!sessionId) return;

  client.post('/analytics/session/end', {
    session_id: sessionId,
    time_spent: timeSpent
  }).catch(err => {
    console.warn('Failed to end session:', err);
  });
}
