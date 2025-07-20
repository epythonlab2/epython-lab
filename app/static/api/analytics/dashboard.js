import {
  fetchPageViews,
  fetchMetrics,
  fetchEngagementSummary,
  fetchEngagementRate
} from './engagement_api.js';

const ctx = document.getElementById('viewsChart').getContext('2d');
let chart;

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
        backgroundColor: '#10b981',  // Tailwind emerald-500
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
          ticks: { color: '#4B5563' }  // Tailwind gray-600
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
 * @param {string} range - one of 'daily', 'weekly', 'monthly'
 */
async function loadAndRenderPageViews(range = 'daily') {
  const data = await fetchPageViews(range);
  renderChart(data);
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
 * Load and display engagement summary (peak hour, peak day, unique visitors)
 */
async function renderEngagementSummary() {
  const data = await fetchEngagementSummary();

  document.getElementById('peakHourRange').textContent = data.peak_hour_range || 'N/A';
  document.getElementById('peakDay').textContent = data.peak_day || 'N/A';
  document.getElementById('uniqueVisitors').textContent = data.unique_visitors || '0';

  if (window.lucide) {
    lucide.createIcons(); // initialize lucide icons
  }
}

/**
 * Load and display engagement rate progress bar and text
 */
async function renderEngagementRate() {
  const rate = await fetchEngagementRate();

  document.getElementById('engagementBar').style.width = rate + '%';
  document.getElementById('engagementText').textContent =
    `${rate}% of visitors engaged with at least one Topic Content`;
}

// Event listeners and initial load
document.addEventListener('DOMContentLoaded', () => {
  loadAndRenderPageViews(); // default 'daily'
  renderDashboardMetrics();
  renderEngagementSummary();
  renderEngagementRate();

  // Listen for range change on views chart
  document.getElementById('rangeSelector').addEventListener('change', e => {
    loadAndRenderPageViews(e.target.value);
  });
});
