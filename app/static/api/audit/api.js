import client from '../axios_client.js';

export const Api = {
  fetchAuditSummary: () => client.get('/audit/audit-summary'),
  fetchLoginTrend: () => client.get('/audit/login-trend'),
  fetchWeeklyActivity: () => client.get('/audit/weekly-activity'),
  fetchDeviceAnalytics: () => client.get('/audit/device-analytics'),
  fetchTopAdmins: () => client.get('/audit/top-admins'),
  fetchInactiveUsers: (page, perPage) => client.get('/audit/inactive-users', { params: { page, per_page: perPage } }),
  fetchGeoLogins: () => client.get('/audit/geo-logins'),
  fetchRecentLogs: () => client.get('/audit/recent-audit-logs'),
  fetchFrequentActions: () => client.get('/audit/frequent-actions'),
};
