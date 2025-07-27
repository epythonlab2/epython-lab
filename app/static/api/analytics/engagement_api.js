// api/analytics/engagement_api.js
import client from '../axios_client.js';

/**
 * Fetch page views analytics for a given time range.
 * @param {string} range - Time range for data ('daily', '7d', '28d', etc.)
 * @returns {Promise<Array>} Array of page view records or empty array on failure.
 */
export async function fetchPageViews(range = 'daily') {
  try {
    const response = await client.get(`/analytics/page-views?range=${range}`);
    return response.data.views || [];
  } catch (error) {
    console.error('Failed to load page views:', error);
    return [];
  }
}

/**
 * Fetch dashboard metrics summary.
 * @returns {Promise<Object>} Object containing user count, today's views, topic contents, and blog posts counts.
 */
export async function fetchMetrics() {
  try {
    const response = await client.get('/analytics/metrics');
    const data = response.data || {};

    return {
      users: data.users || 0,
      viewsToday: data.views_today || 0,
      topicContents: data.topic_contents || 0,
      blogPosts: data.blog_posts || 0,
    };
  } catch (error) {
    console.error('Failed to load dashboard metrics:', error);
    return {
      users: 0,
      viewsToday: 0,
      topicContents: 0,
      blogPosts: 0,
    };
  }
}

/**
 * Fetch summary statistics related to user engagement.
 * @returns {Promise<Object>} Engagement summary including unique visitors, peak hour range, and peak day.
 */
export async function fetchEngagementSummary() {
  try {
    const response = await client.get('/analytics/engagement-summary');
    return response.data || {
      unique_visitors: 0,
      peak_hour_range: 'N/A',
      peak_day: 'N/A',
    };
  } catch (error) {
    console.error('Failed to fetch engagement summary:', error);
    return {
      unique_visitors: 0,
      peak_hour_range: 'N/A',
      peak_day: 'N/A',
    };
  }
}

/**
 * Fetch overall engagement rate percentage.
 * @returns {Promise<number>} Engagement rate percentage, defaults to 0 on failure.
 */
export async function fetchEngagementRate() {
  try {
    const response = await client.get('/analytics/engagement-rate');
    return response.data?.engagement_rate_percent || 0;
  } catch (error) {
    console.error('Failed to fetch engagement rate:', error);
    return 0;
  }
}

/**
 * Fetch daily trend data over a specified range.
 * @param {string} range - Time range for trend data (default '28d').
 * @returns {Promise<Object|null>} Trend data object or null if failed.
 */
export async function loadTrendData(range = '28d') {
  try {
    const response = await client.get(`/analytics/daily-trends?range=${range}`);
    return response.data || null;
  } catch (error) {
    console.error('Failed to load trend data:', error);
    return null;
  }
}

/**
 * Load detailed device and country statistics for engagement views.
 * @param {string} range - Time range for stats (default '28d').
 * @returns {Promise<{data: Object|null, error: string|null}>} Data and error info.
 */
export async function loadDeviceCountryStats(range = '28d') {
  try {
    const response = await client.get(`/analytics/views/stats?range=${range}`);
    return { data: response.data || null, error: null };
  } catch (error) {
    console.error('Failed to load device and country stats:', error);
    return { data: null, error: error.message || 'Unknown error' };
  }
}
