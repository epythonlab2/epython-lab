import { Api } from './api.js';
import { renderLineChart, renderBarChart, renderPieChart } from './chartManager.js';
import { createSummaryCard, renderTableRows, toggleButtons } from './ui.js';
import { inactiveUsersPerPage } from './constants.js';
import { renderInactiveUsersPagination } from './pagination.js';

let inactiveUsersPage = 1;

/**
 * Load audit summary and render cards.
 */
export async function loadAuditSummary() {
  try {
    const { data } = await Api.fetchAuditSummary();
    const container = document.getElementById('audit-summary');
    if (!container) return;

    container.innerHTML = Object.entries(data)
      .map(([type, count]) => createSummaryCard(type, count))
      .join('');
  } catch (error) {
    console.error('Audit summary loading error:', error);
  }
}

/**
 * Load login trend chart.
 */
export async function loadLoginTrend() {
  try {
    const { data } = await Api.fetchLoginTrend();
    renderLineChart('login-trend-chart', data.labels, data.data);
  } catch (error) {
    console.error('Login trend loading error:', error);
  }
}

/**
 * Load weekly activity chart.
 */
export async function loadWeeklyActivity() {
  try {
    const { data } = await Api.fetchWeeklyActivity();
    renderBarChart('weekly-activity-chart', data.labels, data.data);
  } catch (error) {
    console.error('Weekly activity loading error:', error);
  }
}

/**
 * Load device analytics charts.
 */
export async function loadDeviceAnalytics() {
  try {
    const { data } = await Api.fetchDeviceAnalytics();

    const { devices = [], browsers = [], os = [] } = data;

    if (devices.length) {
      renderPieChart(
        'device-chart',
        devices.map(d => d.label.trim()),
        devices.map(d => d.count)
      );
    } else {
      console.warn('No device data available');
    }

    if (browsers.length) {
      renderPieChart(
        'browser-chart',
        browsers.map(b => b.label.trim()),
        browsers.map(b => b.count)
      );
    } else {
      console.warn('No browser data available');
    }

    if (os.length) {
      renderPieChart(
        'os-chart',
        os.map(o => o.label.trim()),
        os.map(o => o.count)
      );
    } else {
      console.warn('No OS data available');
    }
  } catch (error) {
    console.error('Device analytics loading error:', error);
  }
}

/**
 * Load top admins table.
 */
export async function loadTopAdmins() {
  try {
    const { data } = await Api.fetchTopAdmins();
    renderTableRows('top-admins', data, row => `
      <tr>
        <td class="py-2 px-3">${row.username}</td>
        <td class="py-2 px-3">${row.total}</td>
      </tr>
    `);
  } catch (error) {
    console.error('Top admins loading error:', error);
  }
}

/**
 * Load inactive users with pagination.
 * @param {number} [page=1]
 */
export async function loadInactiveUsers(page = 1) {
  if (page < 1) return;
  const containerId = 'inactive-users-pagination';
  const tbodyId = 'inactive-users';

  const container = document.getElementById(containerId);
  const tbody = document.getElementById(tbodyId);
  if (!tbody || !container) return;

  toggleButtons(containerId, true);

  try {
    const { data } = await Api.fetchInactiveUsers(page, inactiveUsersPerPage);
    renderTableRows(tbodyId, data.users, user => `
      <tr>
        <td class="py-2 px-3">${user.username}</td>
        <td class="py-2 px-3">${user.role}</td>
        <td class="py-2 px-3">${user.last_seen}</td>
      </tr>
    `);

    inactiveUsersPage = data.page;
    renderInactiveUsersPagination(containerId, data.page, data.pages);
  } catch (error) {
    console.error('Inactive users loading error:', error);
    tbody.innerHTML = '<tr><td colspan="3" class="py-2 px-3 text-center text-red-600">Failed to load data</td></tr>';
    container.innerHTML = '';
  } finally {
    toggleButtons(containerId, false);
  }
}

/**
 * Load geographic login distribution table.
 */
export async function loadGeoLogins() {
  try {
    const { data } = await Api.fetchGeoLogins();
    renderTableRows('country-distribution', data, row => `
      <tr>
        <td class="py-2 px-3">${row.country}</td>
        <td class="py-2 px-3">${row.count}</td>
      </tr>
    `);
  } catch (error) {
    console.error('Geo logins loading error:', error);
  }
}

/**
 * Load recent audit logs table.
 */
export async function loadRecentLogs() {
  try {
    const { data } = await Api.fetchRecentLogs();
    renderTableRows('audit-table-body', data, log => `
      <tr>
        <td class="py-2 px-3">${log.timestamp}</td>
        <td class="py-2 px-3">${log.actor}</td>
        <td class="py-2 px-3">${log.action_type}</td>
        <td class="py-2 px-3">${log.target || '-'}</td>
        <td class="py-2 px-3 text-gray-600 dark:text-gray-300 max-w-xs truncate">${log.description}</td>
      </tr>
    `);
  } catch (error) {
    console.error('Recent logs loading error:', error);
  }
}

/**
 * Load frequent actions bar chart.
 */
export async function loadFrequentActions() {
  try {
    const { data } = await Api.fetchFrequentActions();
    const labels = data.map(item => item.action);
    const counts = data.map(item => item.count);
    renderBarChart('frequent-actions-chart', labels, counts, 'Actions');
  } catch (error) {
    console.error('Frequent actions loading error:', error);
  }
}

/**
 * Initialize dashboard by loading all components.
 */
export async function initDashboard() {
  await Promise.all([
    loadAuditSummary(),
    loadLoginTrend(),
    // loadActivityByHour(),  // Uncomment if needed
    loadFrequentActions(),
    loadWeeklyActivity(),
    loadDeviceAnalytics(),
    loadTopAdmins(),
    loadInactiveUsers(),
    loadGeoLogins(),
    loadRecentLogs(),
  ]);
}
