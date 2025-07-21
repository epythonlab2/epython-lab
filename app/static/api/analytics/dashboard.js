import {
  fetchPageViews,
  fetchMetrics,
  fetchEngagementSummary,
  fetchEngagementRate,
  loadTrendData
} from './engagement_api.js';

const ctx = document.getElementById('viewsChart').getContext('2d');
let chart;
let trendChart;  // Global trend chart instance

/**
 * Render the page views bar chart
 */
function renderChart(data) {
  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(item => item.title),
      datasets: [{
        label: 'Page Views',
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
}

/**
 * Fetch and render chart data based on range selector
 */
async function loadAndRenderPageViews(range = 'daily') {
  const data = await fetchPageViews(range);
  renderChart(data);
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
  document.getElementById('blogPostsCount').textContent = metrics.blogPosts.toString();
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

  document.getElementById('engagementBar').style.width = rate + '%';
  document.getElementById('engagementText').textContent =
    `${rate}% of visitors engaged with at least one Topic Content`;
}

// Initialize everything on load
document.addEventListener('DOMContentLoaded', () => {
  loadAndRenderPageViews();  // default 'daily'
  renderDashboardMetrics();
  renderEngagementSummary();
  renderEngagementRate();
  loadAndRenderDailyTrend('28d'); // default range

  document.getElementById('rangeSelector').addEventListener('change', e => {
    loadAndRenderPageViews(e.target.value);
  });

  document.getElementById('trendRangeSelector').addEventListener('change', e => {
    loadAndRenderDailyTrend(e.target.value);
  });
});
