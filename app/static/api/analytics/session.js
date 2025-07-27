// analytics/session.js

import client from '../axios_client.js';

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function getDeviceType() {
  const ua = navigator.userAgent;

  // Detect TVs
  const isTV = /TV|SmartTV|AppleTV|GoogleTV|HbbTV|NetCast.TV|WebTV|Xbox|PlayStation/i.test(ua);
  if (isTV) return 'Tv';

  // Detect Mobile phones
  const isMobile = /Mobi|Android.*Mobile|iPhone|BlackBerry|IEMobile|Opera Mini/i.test(ua);
  if (isMobile) return 'Mobile';

  // Detect Tablets:
  //  - iPad, iPadOS 13+ on desktop mode reports Mac, so check for 'Macintosh' + touch support (optional)
  //  - Android tablets usually have 'Android' but NOT 'Mobile'
  //  - Common tablet keywords
  const isTablet = /Tablet|iPad|Nexus 7|Nexus 10|KFAPWI|Silk|PlayBook|Kindle|Touch/i.test(ua)
    || (/Android/i.test(ua) && !/Mobile/i.test(ua)); // Android tablet heuristic

  if (isTablet) return 'Tablet';

  // Default desktop
  return 'Pc';
}


export function trackSessionStart() {
  let sessionId = localStorage.getItem('session_id');
  if (!sessionId) {
    sessionId = generateUUID();
    localStorage.setItem('session_id', sessionId);
  }

  const deviceType = getDeviceType();

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
