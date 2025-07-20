// analytics/search.js

import axios from '../client.js';

export async function logSearch(queryText) {
  const sessionId = localStorage.getItem('session_id');

  try {
    await axios.post('/analytics/search-log', {
      query_text: queryText,
      session_id: sessionId
    });
  } catch (err) {
    console.warn('Search log failed:', err);
  }
}
