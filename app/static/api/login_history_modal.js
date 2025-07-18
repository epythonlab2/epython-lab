// login_history_modal.js

import { loginHistory } from './auth_api.js';

export function initLoginHistoryModal() {
  const modal = document.getElementById('login-history-modal');
  const tbody = document.getElementById('login-history-body');
  const closeBtn = document.getElementById('close-login-history');
  // const closeBtnFooter = document.getElementById('close-login-history-btn');
  const searchInput = document.getElementById('search-history');
  const filterDevice = document.getElementById('filter-device');
  const exportBtn = modal.querySelector('button.bg-green-600');
  let paginationContainer = document.getElementById('login-history-pagination');

  // If the pagination container is not already in your HTML, create it dynamically
  if (!paginationContainer) {
    paginationContainer = document.createElement('div');
    paginationContainer.id = 'login-history-pagination';
    paginationContainer.className = 'mt-2 flex justify-center gap-1 text-sm';
    modal.querySelector('.overflow-x-auto').after(paginationContainer);
  }

  let currentPage = 1;
  const recordsPerPage = 10;
  let totalRecords = 0;
  let currentUserId = null;
  let currentSearch = '';
  let currentDeviceFilter = '';

  async function fetchAndRenderLoginHistory() {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4">Loading...</td></tr>`;

    try {
      const response = await loginHistory(currentUserId, currentPage, recordsPerPage, currentSearch, currentDeviceFilter);
      totalRecords = response.total;

      if (!response.data.length) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4">No login records found.</td></tr>`;
        renderPagination();
        return;
      }

      tbody.innerHTML = response.data.map(log => `
        <tr class="hover:bg-gray-50 dark:hover:bg-gray-800 transition">
          <td class="py-2 px-4" title="${log.login_time}">${log.login_time}</td>
          <td class="py-2 px-4">${log.ip}</td>
          <td class="py-2 px-4  sm:table-cell">${log.country}</td>
          <td class="py-2 px-4  sm:table-cell">
            <span class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold ${log.device === 'Mobile' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}">
              ${log.device}
            </span>
          </td>
          <td class="py-2 px-4  sm:table-cell">${log.os}</td>
          <td class="py-2 px-4  sm:table-cell">${log.browser}</td>
        </tr>
      `).join('');

      renderPagination();
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-red-600 text-center py-4">Error loading data.</td></tr>`;
      console.error(err);
    }
  }

  function renderPagination() {
    const totalPages = Math.ceil(totalRecords / recordsPerPage);
    if (totalPages <= 1) {
      paginationContainer.innerHTML = '';
      return;
    }
    let buttonsHtml = '';
    for (let i = 1; i <= totalPages; i++) {
      buttonsHtml += `<button
        class="px-3 py-1 rounded ${i === currentPage ? 'bg-blue-600 text-white' : 'bg-gray-100 hover:bg-gray-200'}"
        data-page="${i}">
        ${i}
      </button>`;
    }
    paginationContainer.innerHTML = buttonsHtml;

    paginationContainer.querySelectorAll('button').forEach(btn => {
      btn.addEventListener('click', () => {
        currentPage = Number(btn.getAttribute('data-page'));
        fetchAndRenderLoginHistory();
      });
    });
  }

  function openModal(userId) {
    currentUserId = userId;
    currentPage = 1;
    currentSearch = '';
    currentDeviceFilter = '';
    searchInput.value = '';
    filterDevice.value = '';
    modal.dataset.userId = userId;
    modal.classList.remove('hidden');
    fetchAndRenderLoginHistory();
  }

  function closeModal() {
    modal.classList.add('hidden');
    currentUserId = null;
  }


  closeBtn.addEventListener('click', closeModal);
  // closeBtnFooter.addEventListener('click', closeModal);

  searchInput.addEventListener('input', () => {
    currentSearch = searchInput.value.trim();
    currentPage = 1;
    fetchAndRenderLoginHistory();
  });

  filterDevice.addEventListener('change', () => {
    currentDeviceFilter = filterDevice.value;
    currentPage = 1;
    fetchAndRenderLoginHistory();
  });

  // exportBtn.addEventListener('click', exportCSV);

  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  return { openModal, closeModal };
}
