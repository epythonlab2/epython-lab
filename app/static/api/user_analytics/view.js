// analytics/view.js

import client from '../axios_client.js';

export function trackSubTopicView(subtopicId, timeSpentSeconds, scrollDepthPercent) {
  const sessionId = localStorage.getItem('session_id');
  if (!sessionId) {
    console.warn('No session_id found for subtopic view tracking.');
    return;
  }

  client.post('/analytics/subtopic/view', {
    session_id: sessionId,
    subtopic_id: subtopicId,
    time_spent_seconds: timeSpentSeconds,
    scroll_depth_percent: scrollDepthPercent
  }).catch(err => {
    console.warn('Failed to record subtopic view:', err);
  });
}
