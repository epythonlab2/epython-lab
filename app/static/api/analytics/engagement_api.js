// api/analytics/engagement_api.js
import client from '../axios_client.js';

export async function fetchPageViews(range = 'daily') {
  try {
    const res = await client.get(`/analytics/page-views?range=${range}`);
    return res.data.views;  // ✅ return data for external render
  } catch (err) {
    console.error('Failed to load data:', err);
    return [];
  }
}

export async function fetchMetrics() {
  try {
    const res = await client.get('/analytics/metrics');  // corrected URL
    const data = res.data;

    return {
      users: data.users,
      viewsToday: data.views_today,
      topicContents: data.topic_contents,
      blogPosts: data.blog_posts
    };
  } catch (err) {
    console.error('Failed to load dashboard metrics:', err);
    return {
      users: 0,
      viewsToday: 0,
      topicContents: 0,
      blogPosts: 0
    };
  }
}
export async function fetchEngagementSummary() {
  try {
    const res = await client.get('/analytics/engagement-summary');
    return res.data;
  } catch (err) {
    console.error('Failed to fetch engagement summary:', err);
    return {
      unique_visitors: 0,
      peak_hour_range: 'N/A',
      peak_day: 'N/A',
    };
  }
}

export async function fetchEngagementRate() {
  try {
    const res = await client.get('/analytics/engagement-rate');
    return res.data.engagement_rate_percent || 0;
  } catch (err) {
    console.error('Failed to fetch engagement rate:', err);
    return 0;
  }
}

export async function loadTrendData(range = '28d') {
  try {
    const res = await client.get(`/analytics/daily-trends?range=${range}`);
    return res.data; // Use res.data directly
  } catch (err) {
    console.error("Failed to load trend data:", err);
  }
}
