import client from './axios_client.js';

const summaryColors = {
  create: 'bg-blue-100 text-blue-600',
  update: 'bg-yellow-100 text-yellow-600',
  delete: 'bg-red-100 text-red-600'
};

const chartInstances = {};  // Hold chart instances to destroy before re-render

function destroyChart(id) {
  if (chartInstances[id]) {
    chartInstances[id].destroy();
    delete chartInstances[id];
  }
}

function createCard(type, count) {
  return `
    <div class="flex items-center bg-white dark:bg-gray-900 p-4 rounded-xl shadow-md">
      <div class="p-3 ${summaryColors[type] || 'bg-gray-100 text-gray-600'} rounded-full">
        <i data-lucide="activity" class="w-6 h-6"></i>
      </div>
      <div class="ml-4">
        <h2 class="text-sm text-gray-500 dark:text-gray-400 capitalize">${type}</h2>
        <p class="text-xl font-bold text-gray-700 dark:text-white">${count}</p>
      </div>
    </div>`;
}

async function loadAuditSummary() {
  try {
    const res = await client.get('/audit/audit-summary');
    const container = document.getElementById('audit-summary');
    container.innerHTML = Object.entries(res.data)
      .map(([type, count]) => createCard(type, count))
      .join('');
  } catch (err) {
    console.error('Audit summary loading error:', err);
  }
}

function renderLineChart(canvasId, labels, data) {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId).getContext('2d');
  chartInstances[canvasId] = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Logins',
        data,
        fill: true,
        backgroundColor: 'rgba(59,130,246,0.1)',
        borderColor: '#3B82F6',
        tension: 0.3,
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
}

async function loadLoginTrend() {
  try {
    const res = await client.get('/audit/login-trend');
    renderLineChart('login-trend-chart', res.data.labels, res.data.data);
  } catch (err) {
    console.error('Login trend loading error:', err);
  }
}

function renderBarChart(canvasId, labels, data) {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId).getContext('2d');
  chartInstances[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Activity',
        data,
        backgroundColor: '#3B82F6'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}

// async function loadActivityByHour() {
//   try {
//     const res = await client.get('/audit/activity-by-hour');
//     renderBarChart('activity-hour-chart', res.data.labels, res.data.data);
//   } catch (err) {
//     console.error('Activity by hour loading error:', err);
//   }
// }

async function loadWeeklyActivity() {
  try {
    const res = await client.get('/audit/weekly-activity');
    renderBarChart('weekly-activity-chart', res.data.labels, res.data.data);
  } catch (err) {
    console.error('Weekly activity loading error:', err);
  }
}

function renderPieChart(id, labels, data, colorSet) {
  destroyChart(id);
  const canvas = document.getElementById(id);
  if (!canvas) {
    console.error(`Canvas with id '${id}' not found.`);
    return;
  }
  const ctx = canvas.getContext('2d');
  chartInstances[id] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colorSet || ['#60a5fa', '#34d399', '#fbbf24', '#f87171', '#a78bfa']
      }]
    },
    options: { responsive: true, maintainAspectRatio: false, cutout: '65%' }
  });
}

async function loadDeviceAnalytics() {
  try {
    const res = await client.get('/audit/device-analytics');

    const devices = res.data.devices || [];
    const browsers = res.data.browsers || [];
    const os = res.data.os || [];

    if (devices.length > 0) {
      renderPieChart(
        'device-chart',
        devices.map(d => d.label.trim()),
        devices.map(d => d.count)
      );
    } else {
      console.warn('No device data available');
    }

    if (browsers.length > 0) {
      renderPieChart(
        'browser-chart',
        browsers.map(b => b.label.trim()),
        browsers.map(b => b.count)
      );
    } else {
      console.warn('No browser data available');
    }

    if (os.length > 0) {
      renderPieChart(
        'os-chart',
        os.map(o => o.label.trim()),
        os.map(o => o.count)
      );
    } else {
      console.warn('No OS data available');
    }
  } catch (err) {
    console.error('Device analytics loading error:', err);
  }
}

async function loadTopAdmins() {
  try {
    const res = await client.get('/audit/top-admins');
    const tbody = document.getElementById('top-admins');
    tbody.innerHTML = res.data.map(row => `
      <tr>
        <td class="py-2 px-3">${row.username}</td>
        <td class="py-2 px-3">${row.total}</td>
      </tr>`).join('');
  } catch (err) {
    console.error('Top admins loading error:', err);
  }
}

let inactiveUsersPage = 1;
const inactiveUsersPerPage = 20;

async function loadInactiveUsers(page = 1) {
  if (page < 1) return;
  const container = document.getElementById('inactive-users-pagination');
  const tbody = document.getElementById('inactive-users');
  if (!tbody || !container) return;

  // Disable pagination buttons during loading
  container.querySelectorAll('button').forEach(btn => btn.disabled = true);

  try {
    const res = await client.get('/audit/inactive-users', {
      params: { page, per_page: inactiveUsersPerPage }
    });
    const data = res.data;

    // Render rows
    tbody.innerHTML = data.users.map(user => `
      <tr>
        <td class="py-2 px-3">${user.username}</td>
        <td class="py-2 px-3">${user.role}</td>
        <td class="py-2 px-3">${user.last_seen}</td>
      </tr>
    `).join('');

    inactiveUsersPage = data.page;

    renderInactiveUsersPagination(data.page, data.pages);

  } catch (err) {
    console.error('Inactive users loading error:', err);
    tbody.innerHTML = '<tr><td colspan="3" class="py-2 px-3 text-center text-red-600">Failed to load data</td></tr>';
    container.innerHTML = '';
  }
}

function renderInactiveUsersPagination(currentPage, totalPages) {
  const container = document.getElementById('inactive-users-pagination');
  if (!container) return;

  if (totalPages <= 5) {
    container.innerHTML = '';  // Hide pagination if unnecessary
    return;
  }

  container.innerHTML = '';

  // Previous button
  const prevBtn = document.createElement('button');
  prevBtn.textContent = 'Previous';
  prevBtn.className = 'btn px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed';
  prevBtn.disabled = currentPage === 1;
  prevBtn.setAttribute('aria-disabled', prevBtn.disabled);
  prevBtn.addEventListener('click', () => loadInactiveUsers(currentPage - 1));
  container.appendChild(prevBtn);

  // Page info
  const pageInfo = document.createElement('span');
  pageInfo.className = 'mx-2 text-gray-700 dark:text-gray-300';
  pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
  container.appendChild(pageInfo);

  // Next button
  const nextBtn = document.createElement('button');
  nextBtn.textContent = 'Next';
  nextBtn.className = 'btn px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed';
  nextBtn.disabled = currentPage === totalPages;
  nextBtn.setAttribute('aria-disabled', nextBtn.disabled);
  nextBtn.addEventListener('click', () => loadInactiveUsers(currentPage + 1));
  container.appendChild(nextBtn);
}

// // Initial load on DOM ready
// document.addEventListener('DOMContentLoaded', () => {
//   loadInactiveUsers(inactiveUsersPage);
// });
//
// // Optional: expose for debugging/testing
// window.loadInactiveUsers = loadInactiveUsers;


async function loadGeoLogins() {
  try {
    const res = await client.get('/audit/geo-logins');
    const tbody = document.getElementById('country-distribution');
    tbody.innerHTML = res.data.map(row => `
      <tr>
        <td class="py-2 px-3">${row.country}</td>
        <td class="py-2 px-3">${row.count}</td>
      </tr>`).join('');
  } catch (err) {
    console.error('Geo logins loading error:', err);
  }
}

async function loadRecentLogs() {
  try {
    const res = await client.get('/audit/recent-audit-logs');
    const tbody = document.getElementById('audit-table-body');
    tbody.innerHTML = res.data.map(log => `
      <tr>
        <td class="py-2 px-3">${log.timestamp}</td>
        <td class="py-2 px-3">${log.actor}</td>
        <td class="py-2 px-3">${log.action_type}</td>
        <td class="py-2 px-3">${log.target || '-'}</td>
        <td class="py-2 px-3 text-gray-600 dark:text-gray-300 max-w-xs truncate">${log.description}</td>
      </tr>`).join('');
  } catch (err) {
    console.error('Recent logs loading error:', err);
  }
}

async function loadFrequentActions() {
  try {
    const res = await client.get('/audit/frequent-actions');
    const labels = res.data.map(item => item.action);
    const data = res.data.map(item => item.count);

    renderBarChart('frequent-actions-chart', labels, data);
  } catch (err) {
    console.error('Frequent actions loading error:', err);
  }
}

async function initDashboard() {
  await Promise.all([
    loadAuditSummary(),
    loadLoginTrend(),
    // loadActivityByHour(),
    loadFrequentActions(),
    loadWeeklyActivity(),
    loadDeviceAnalytics(),
    loadTopAdmins(),
    loadInactiveUsers(),
    loadGeoLogins(),
    loadRecentLogs(),
  ]);
}

document.addEventListener('DOMContentLoaded', initDashboard);
