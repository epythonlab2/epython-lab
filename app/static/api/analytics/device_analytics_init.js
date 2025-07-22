import { loadDeviceCountryStats } from './engagement_api.js';

// Color mapping per category for chart styling
const colorMap = {
  device_type: '#10B981',  // Green
  os: '#2563EB',           // Blue
  browser: '#7C3AED',      // Purple
  country: '#FBBF24',      // Yellow
};

// Human-readable titles for categories
const categoryTitleMap = {
  os: "OS Type",
  device_type: "Device Type",
  country: "Geography",
  browser: "Browser",
};

// Engagement Breakdown Module
const EngagementBreakdown = (() => {
  const chartInstances = {}; // Stores Chart.js instances to allow cleanup

  // Resolve appropriate color for a category
  function getColor(category) {
    return colorMap[category.toLowerCase().replace(/-/g, '_')] || '#4F46E5'; // Fallback Indigo
  }

  // Show full list in a modal when "See All" is clicked
  function expandList(category, items, total) {
    const modal = document.getElementById('breakdownModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalList = document.getElementById('modalList');

    modalTitle.textContent = categoryTitleMap[category] || category;
    modalList.innerHTML = '';

    const color = getColor(category);

    items.forEach(i => {
      const percent = total ? ((i.views / total) * 100).toFixed(1) : 0;
      const li = document.createElement('li');
      li.className = "flex items-center justify-between";
      li.innerHTML = `
        <span class="text-gray-700 font-medium w-1/3 truncate" title="${i.key}">${i.key}</span>
        <div class="flex-1 mx-4 bg-gray-200 rounded-full h-4 overflow-hidden">
          <div style="width: ${percent}%; background-color: ${color}; height: 1rem; border-radius: 9999px;"></div>
        </div>
        <span class="text-gray-800 font-semibold w-20 text-right">${i.views} views</span>
      `;
      modalList.appendChild(li);
    });

    modal.classList.remove('hidden');
  }

  // Render a horizontal bar chart for the category
  function renderBreakdownChart(category, items) {
    const container = document.getElementById('engagementBreakdownContainer');
    if (!container) return;

    const totalViews = items.reduce((sum, i) => sum + i.views, 0);
    const color = getColor(category);
    const canvasId = `${category}-chart`;
    const topItems = items.slice(0, 3); // Show top 3 items by default

    const labels = topItems.map(i => i.key);
    const dataValues = topItems.map(i => i.views);

    // Reuse or create new card container
    let card = document.getElementById(`${category}-card`);
    if (!card) {
      card = document.createElement('section');
      card.id = `${category}-card`;
      card.className = "bg-white p-6 rounded-xl shadow hover:shadow-md transition-shadow";
      container.appendChild(card);
    }

    // Set card content with canvas
    card.innerHTML = `
      <h3 class="text-lg font-semibold text-gray-800 mb-4 capitalize">${categoryTitleMap[category] || category}</h3>
      <canvas id="${canvasId}" height="150"></canvas>
    `;

    // Destroy old chart to prevent memory leaks
    if (chartInstances[canvasId]) {
      chartInstances[canvasId].destroy();
      delete chartInstances[canvasId];
    }

    const ctx = card.querySelector(`#${canvasId}`).getContext('2d');

    // Initialize Chart.js bar chart
    chartInstances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Views',
          data: dataValues,
          backgroundColor: color,
          borderRadius: 5,
          maxBarThickness: 30,
        }]
      },
      options: {
        indexAxis: 'y',  // Horizontal bars
        responsive: true,
        scales: {
          x: {
            beginAtZero: true,
            ticks: { precision: 0 },
            grid: { display: false }  // Hide grid lines
          },
          y: {
            grid: { display: false }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => `${ctx.parsed.x} views`
            }
          }
        }
      }
    });

    // Add "See All" button if more than 3 items
    if (items.length > 3) {
      const expandBtn = document.createElement('button');
      expandBtn.textContent = `See All (${items.length})`;
      expandBtn.className = 'expand-btn mt-4 text-indigo-600 hover:underline text-sm font-medium';
      expandBtn.addEventListener('click', () => expandList(category, items, totalViews));
      card.appendChild(expandBtn);
    }
  }

  // Fetch and render analytics data
  async function updateEngagementStats(range = '28d') {
    const container = document.getElementById('engagementBreakdownContainer');
    if (!container) return;

    // Fade cards during load
    container.querySelectorAll('section').forEach(card => {
      card.style.opacity = '0.5';
      card.style.pointerEvents = 'none';
    });

    try {
      const { data, error } = await loadDeviceCountryStats(range);

      if (error) {
        container.innerHTML = `<p class="text-red-600">Error loading analytics: ${error}</p>`;
        return;
      }
      if (!data) {
        container.innerHTML = '<p class="text-gray-500">No analytics data available.</p>';
        return;
      }

      const categories = ['device_type', 'os', 'browser', 'country'];

      for (const category of categories) {
        if (Array.isArray(data[category])) {
          const items = data[category]
            .filter(item => item.views > 0)
            .sort((a, b) => b.views - a.views);

          if (items.length > 0) {
            renderBreakdownChart(category, items);
          } else {
            const card = document.getElementById(`${category}-card`);
            if (card) {
              card.innerHTML = `<p class="text-gray-500">No data for ${categoryTitleMap[category] || category}</p>`;
            }
          }
        }
      }
    } catch (err) {
      container.innerHTML = `<p class="text-red-600">Failed to load analytics: ${err.message}</p>`;
    } finally {
      // Restore card interactivity
      container.querySelectorAll('section').forEach(card => {
        card.style.opacity = '1';
        card.style.pointerEvents = 'auto';
      });
    }
  }

  // Bind range selector dropdown
  function bindRangeSelector(rangeSelectId = 'rangeSelect') {
    const container = document.getElementById('engagementBreakdownContainer');
    const rangeSelect = container?.parentElement?.querySelector(`#${rangeSelectId}`);
    if (!rangeSelect) {
      console.error('rangeSelect dropdown not found.');
      return;
    }

    let debounceTimer;
    rangeSelect.addEventListener('change', e => {
      e.preventDefault();
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => updateEngagementStats(e.target.value), 300);
    });
  }

  // Setup modal close handlers
  function initModalHandlers() {
    const modal = document.getElementById('breakdownModal');
    if (!modal) return;

    const closeBtn = document.getElementById('closeModalBtn');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
    }

    modal.addEventListener('click', (e) => {
      if (e.target.id === 'breakdownModal') {
        modal.classList.add('hidden');
      }
    });
  }

  // Public init function
  function init() {
    document.addEventListener('DOMContentLoaded', () => {
      bindRangeSelector();
      initModalHandlers();

      const rangeSelect = document.getElementById('rangeSelect');
      if (rangeSelect) updateEngagementStats(rangeSelect.value);
    });
  }

  return { init };
})();

// Initialize the module
EngagementBreakdown.init();
