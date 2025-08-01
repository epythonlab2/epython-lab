import {
  fetchTopContentViews,
  fetchMetrics,
  fetchEngagementSummary,
  fetchEngagementRate,
  loadTrendData
} from './engagement_api.js';

const ctx = document.getElementById('viewsChart')?.getContext('2d');
let chart;
let trendChart;  // Optional: for another chart elsewhere

/**
 * Render the Top Content views bar chart (top 3)
 */
async function renderTopContentChart(rawData) {
  if (!ctx) return;

  const data = rawData.slice(0, 3); // Show only top 3

  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(item => item.subtopic_title),
      datasets: [{
        label: 'Top Content Views',
        data: data.map(item => item.views),
        backgroundColor: '#10b981',
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.raw} views`
          }
        }
      },
      scales: {
        x: {
          ticks: { color: '#4B5563' }
        },
        y: {
          beginAtZero: true,
          ticks: { stepSize: 10, color: '#4B5563' }
        }
      }
    }
  });

  // Optional: render table if needed
  renderTopContentTable(data);
}

 function renderTopContentTable(data) {
  const tbody = document.getElementById('topContentsTable');
  tbody.innerHTML = '';

  data.forEach((row, index) => {
  const scrollDist = row.scroll_distribution || {};
  const scrollHtml = `
    0–25%: ${scrollDist['0-25%'] || 0},\n
    25–50%: ${scrollDist['25-50%'] || 0},\n
    50–75%: ${scrollDist['50-75%'] || 0},\n
    75–100%: ${scrollDist['75-100%'] || 0}
  `;

  const tr = document.createElement('tr');
  tr.className = 'border-b hover:bg-gray-50';

  tr.innerHTML = `
    <td class="py-2 px-3 text-gray-500">${index + 1}</td>
    <td class="py-2 px-3">${row.topic_title || '-'}</td>
    <td class="py-2 px-3">${row.subtopic_title || row.title}</td>
    <td class="py-2 px-3">${row.views}</td>
    <td class="py-2 px-3 whitespace-pre-line font-mono text-sm">${scrollHtml}</td>
    <td class="py-2 px-3">
      ${formatTime(row.avg_time_spent_seconds)}
    </td>
  `;

  tbody.appendChild(tr);
});
}

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '0s';

  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  const parts = [];
  if (hrs) parts.push(`${hrs}h`);
  if (mins) parts.push(`${mins}m`);
  if (secs || (!hrs && !mins)) parts.push(`${secs}s`);

  return parts.join(' ');
}




/**
 * Fetch and render chart data based on range selector
 */
async function loadAndRenderTopContentViews(range = 'daily') {
  const data = await fetchTopContentViews(range);
  renderTopContentChart(data);
}

/**
 * Fetch and render the trend chart (line chart)
 */
async function loadAndRenderDailyTrend(range = '28d') {
  const data = await loadTrendData(range);
  renderTrendChart(data);
}

function renderTrendChart(data) {
  const ctx = document.getElementById('trendChart').getContext('2d');

  if (trendChart) trendChart.destroy();

  trendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [
        {
          label: 'Views',
          data: data.views,
          borderColor: 'rgba(20, 184, 166, 1)',
          backgroundColor: 'rgba(20, 184, 166, 0.15)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointBackgroundColor: 'rgba(20, 184, 166, 1)',
        },
        {
          label: 'Active Users',
          data: data.users,
          borderColor: 'rgba(59, 130, 246, 1)',
          backgroundColor: 'rgba(59, 130, 246, 0.15)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointBackgroundColor: 'rgba(59, 130, 246, 1)',
        },
        {
          label: 'Avg. Time Spent (min)',
          data: Array.isArray(data.time_spent)
            ? data.time_spent.map(seconds => (seconds / 60).toFixed(2))
            : [],
          borderColor: 'rgba(234, 179, 8, 1)',
          backgroundColor: 'rgba(234, 179, 8, 0.15)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointBackgroundColor: 'rgba(234, 179, 8, 1)',
          yAxisID: 'y1',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      stacked: false,
      scales: {
        y: {
          beginAtZero: true,
          position: 'left',
          title: {
            display: true,
            text: 'Count',
            font: {
              size: 14,
              weight: 'bold',
            },
          },
          grid: {
            color: 'rgba(229, 231, 235, 0.5)', // light gray grid
            borderDash: [3, 3],
          },
        },
        y1: {
          beginAtZero: true,
          position: 'right',
          title: {
            display: true,
            text: 'Time (min)',
            font: {
              size: 14,
              weight: 'bold',
            },
          },
          grid: {
            drawOnChartArea: false,
          },
        },
        x: {
          ticks: {
            autoSkip: true,
            maxTicksLimit: 7, // adjust depending on chart width
            font: {
              size: 12,
            },
          },
          grid: {
            color: 'rgba(243, 244, 246, 0.5)',
          },
        }
      },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            font: {
              size: 13,
            },
            boxWidth: 14,
            padding: 16,
          },
        },
        tooltip: {
          backgroundColor: '#111827',
          titleFont: { size: 13, weight: 'bold' },
          bodyFont: { size: 12 },
          bodyColor: '#F9FAFB',
          borderColor: '#E5E7EB',
          borderWidth: 1,
          padding: 10,
          cornerRadius: 6,
        },
      },
    },
  });
}

/**
 * Load and display dashboard summary metrics
 */
async function renderDashboardMetrics() {
  const metrics = await fetchMetrics();

  document.getElementById('usersCount').textContent = metrics.users.toString();
  document.getElementById('viewsTodayCount').textContent = metrics.viewsToday.toString();
  document.getElementById('topicContentsCount').textContent = metrics.topicContents.toString();
  document.getElementById('newUsersCount').textContent = metrics.newUsersCount.toString();
}

/**
 * Load and display engagement summary
 */
async function renderEngagementSummary() {
  const data = await fetchEngagementSummary();

  document.getElementById('peakHourRange').textContent = data.peak_hour_range || 'N/A';
  document.getElementById('peakDay').textContent = data.peak_day || 'N/A';
  document.getElementById('uniqueVisitors').textContent = data.unique_visitors || '0';

  // if (window.lucide) lucide.createIcons();
}

/**
 * Load and display engagement rate
 */
async function renderEngagementRate() {
  const rate = await fetchEngagementRate();

  const textEl = document.getElementById('engagementBar');
  textEl.style.width = rate + '%';
  textEl.setAttribute('data-tooltip', `${rate}% of visitors interacted with at least one Topic Content`);
}

// Initialize everything on load
document.addEventListener('DOMContentLoaded', () => {
  loadAndRenderTopContentViews();  // default 'daily'
  renderDashboardMetrics();
  renderEngagementSummary();
  renderEngagementRate();
  loadAndRenderDailyTrend('28d'); // default range

  document.getElementById('topContentSelector').addEventListener('change', e => {
    loadAndRenderTopContentViews(e.target.value);
  });

  document.getElementById('topContentSelector').addEventListener('change', e => {
    loadAndRenderTopContentViews(e.target.value);
  });

  document.getElementById('trendRangeSelector').addEventListener('change', e => {
    loadAndRenderDailyTrend(e.target.value);
  });
});

// Top Content Table Modal toggle
document.getElementById('seeAllBtn').addEventListener('click', () => {
  document.getElementById('topContentsModal').classList.remove('hidden');
});
document.getElementById('closeTopModalBtn').addEventListener('click', () => {
  document.getElementById('topContentsModal').classList.add('hidden');
});
// Tooltip for Engagement rate
const tooltip = document.getElementById('tooltip');

document.addEventListener('mouseover', e => {
  const el = e.target.closest('.tooltip-trigger');
  if (!el) return;

  const text = el.getAttribute('data-tooltip');
  if (!text) return;

  tooltip.textContent = text;
  const rect = el.getBoundingClientRect();
  const tooltipRect = tooltip.getBoundingClientRect();

  const top = rect.top + window.scrollY - tooltipRect.height - 8;
  const left = rect.left + rect.width / 2 - tooltipRect.width / 2;

  tooltip.style.top = `${top}px`;
  tooltip.style.left = `${left}px`;
  tooltip.classList.remove('invisible', 'opacity-0');
  tooltip.classList.add('visible', 'opacity-100');
});

document.addEventListener('mouseout', e => {
  if (e.target.closest('.tooltip-trigger')) {
    tooltip.classList.add('invisible', 'opacity-0');
    tooltip.classList.remove('visible', 'opacity-100');
  }
});
