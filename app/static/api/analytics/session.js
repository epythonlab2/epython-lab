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

export function trackSubTopicView(subtopicId, timeSpentSeconds, scrollDepthPercent) {
  const sessionId = localStorage.getItem('session_id');
  if (!sessionId) {
    console.warn('No session_id found for subtopic view tracking.');
    return;
  }

  // Only send once per page load
  if (window.hasTrackedSubtopicView) return;
  window.hasTrackedSubtopicView = true;

  // const viewEventId = generateUUID();

  client.post('/analytics/subtopic/view', {
    session_id: sessionId,
    subtopic_id: subtopicId,
    time_spent_seconds: timeSpentSeconds,
    scroll_depth_percent: scrollDepthPercent,
  }).catch(err => {
    console.warn('Failed to record subtopic view:', err);
  });
}
