import { summaryColors } from './constants.js';

/**
 * Create an HTML card element string for audit summary,
 * with colors matching the chart palette.
 * @param {string} type
 * @param {number} count
 * @returns {string}
 */
export function createSummaryCard(type, count) {
  const colorClasses = summaryColors[type] || 'bg-gray-100 text-gray-600';
  const iconMap = {
    create: 'plus-circle',
    update: 'refresh-cw',
    delete: 'trash-2',
    login: 'log-in',
    // extend as needed
  };
  const icon = iconMap[type] || 'activity';

  return `
    <div class="flex items-center bg-white dark:bg-gray-900 p-4 rounded-xl shadow-md">
      <div class="p-3 ${colorClasses} rounded-full">
        <i data-lucide="${icon}" class="w-6 h-6"></i>
      </div>
      <div class="ml-4">
        <h2 class="text-sm text-gray-500 dark:text-gray-400 capitalize">${type}</h2>
        <p class="text-xl font-bold text-gray-700 dark:text-white">${count}</p>
      </div>
    </div>
  `;
}


/**
 * Render a table body with rows from data array and row template function.
 * @param {string} tbodyId
 * @param {Array<any>} data
 * @param {(item: any) => string} rowTemplate
 */
export function renderTableRows(tbodyId, data, rowTemplate) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) {
    console.error(`Table body element with id '${tbodyId}' not found.`);
    return;
  }
  tbody.innerHTML = data.map(rowTemplate).join('');
}

/**
 * Disable or enable all buttons within a container.
 * @param {string} containerId
 * @param {boolean} disabled
 */
export function toggleButtons(containerId, disabled) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.querySelectorAll('button').forEach(btn => {
    btn.disabled = disabled;
    btn.setAttribute('aria-disabled', disabled);
  });
}
