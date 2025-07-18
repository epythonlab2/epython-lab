const chartInstances = {};

/**
 * Destroy existing chart instance by ID if any.
 * @param {string} id - Canvas element ID
 */
export function destroyChart(id) {
  if (chartInstances[id]) {
    chartInstances[id].destroy();
    delete chartInstances[id];
  }
}

/**
 * Render a modern, responsive line chart with gradient and animation.
 * @param {string} canvasId
 * @param {Array<string>} labels
 * @param {Array<number>} data
 */
export function renderLineChart(canvasId, labels, data) {
  destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) {
    console.error(`Canvas element with id '${canvasId}' not found.`);
    return;
  }
  const ctx = canvas.getContext('2d');

  // Gradient fill for line chart
  const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
  gradient.addColorStop(0, 'rgba(59, 130, 246, 0.4)');
  gradient.addColorStop(1, 'rgba(59, 130, 246, 0)');

  chartInstances[canvasId] = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Logins',
        data,
        fill: true,
        backgroundColor: gradient,
        borderColor: '#3B82F6',
        borderWidth: 3,
        pointRadius: 6,
        pointHoverRadius: 8,
        pointBackgroundColor: '#3B82F6',
        tension: 0.4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 1200,
        easing: 'easeOutQuart',
      },
      interaction: {
        mode: 'nearest',
        intersect: false,
      },
      plugins: {
        tooltip: {
          enabled: true,
          backgroundColor: '#1E40AF',
          titleColor: '#fff',
          bodyColor: '#fff',
          cornerRadius: 6,
          padding: 10,
          displayColors: false,
          callbacks: {
            label: ctx => `${ctx.parsed.y} logins`,
          },
        },
        legend: {
          display: true,
          labels: {
            color: '#334155',
            font: { size: 14, weight: '600' },
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#64748b', maxRotation: 45, minRotation: 30 },
        },
        y: {
          beginAtZero: true,
          grid: {
            color: '#e2e8f0',
            borderDash: [5, 5],
          },
          ticks: { color: '#64748b' },
        },
      },
    },
  });
}

/**
 * Render a modern, responsive bar chart with rounded bars and animation.
 * @param {string} canvasId
 * @param {Array<string>} labels
 * @param {Array<number>} data
 * @param {string} label - Dataset label
 */
export function renderBarChart(canvasId, labels, data, label = 'Activity') {
  destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) {
    console.error(`Canvas element with id '${canvasId}' not found.`);
    return;
  }
  const ctx = canvas.getContext('2d');

  // Gradient fill for bars
  const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
  gradient.addColorStop(0, '#3B82F6');
  gradient.addColorStop(1, '#2563eb');

  chartInstances[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label,
        data,
        backgroundColor: gradient,
        borderRadius: 6,
        maxBarThickness: 40,
        hoverBackgroundColor: '#2563eb',
        hoverBorderColor: '#1D4ED8',
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 1000,
        easing: 'easeOutQuart',
      },
      plugins: {
        tooltip: {
          backgroundColor: '#1E40AF',
          titleColor: '#fff',
          bodyColor: '#fff',
          cornerRadius: 6,
          padding: 10,
          displayColors: false,
        },
        legend: {
          display: true,
          labels: {
            color: '#334155',
            font: { size: 14, weight: '600' },
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#64748b' },
        },
        y: {
          beginAtZero: true,
          grid: {
            color: '#e2e8f0',
            borderDash: [5, 5],
          },
          ticks: { color: '#64748b' },
        },
      },
    },
  });
}

/**
 * Render a modern, responsive doughnut chart with animation.
 * @param {string} canvasId
 * @param {Array<string>} labels
 * @param {Array<number>} data
 * @param {Array<string>} [colorSet]
 */
export function renderPieChart(canvasId, labels, data, colorSet) {
  destroyChart(canvasId);
  const canvas = document.getElementById(canvasId);
  if (!canvas) {
    console.error(`Canvas element with id '${canvasId}' not found.`);
    return;
  }
  const ctx = canvas.getContext('2d');

  const defaultColors = [
    '#60a5fa', // blue-400
    '#34d399', // green-400
    '#fbbf24', // yellow-400
    '#f87171', // red-400
    '#a78bfa', // purple-400
  ];

  chartInstances[canvasId] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colorSet || defaultColors,
        borderWidth: 2,
        borderColor: '#fff',
        hoverOffset: 30,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      animation: {
        animateRotate: true,
        animateScale: true,
        duration: 1000,
        easing: 'easeOutQuart',
      },
      plugins: {
        tooltip: {
          backgroundColor: '#1E40AF',
          titleColor: '#fff',
          bodyColor: '#fff',
          cornerRadius: 6,
          padding: 10,
          displayColors: true,
        },
        legend: {
          position: 'top',
          labels: {
            color: '#334155',
            font: { size: 14 },
            padding: 20,
          },
        },
      },
    },
  });
}
