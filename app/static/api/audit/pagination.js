import { loadInactiveUsers } from './dashboard.js';

/**
 * Render pagination controls for inactive users.
 * @param {string} containerId
 * @param {number} currentPage
 * @param {number} totalPages
 */
export function renderInactiveUsersPagination(containerId, currentPage, totalPages) {
  const container = document.getElementById(containerId);
  if (!container) return;

  // Hide pagination if not needed or less than or equal to 5 pages
  if (totalPages <= 5) {
    container.innerHTML = '';
    return;
  }

  container.innerHTML = '';

  const createButton = (text, disabled, onClick) => {
    const btn = document.createElement('button');
    btn.textContent = text;
    btn.className = 'btn px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed';
    btn.disabled = disabled;
    btn.setAttribute('aria-disabled', disabled);
    btn.addEventListener('click', onClick);
    return btn;
  };

  const prevBtn = createButton('Previous', currentPage === 1, () => loadInactiveUsers(currentPage - 1));
  const nextBtn = createButton('Next', currentPage === totalPages, () => loadInactiveUsers(currentPage + 1));

  const pageInfo = document.createElement('span');
  pageInfo.className = 'mx-2 text-gray-700 dark:text-gray-300';
  pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;

  container.appendChild(prevBtn);
  container.appendChild(pageInfo);
  container.appendChild(nextBtn);
}
