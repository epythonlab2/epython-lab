import { fetchUsers, deleteUser } from '/static/api/user_api.js';

export function initUserTable({
  tableBodyId = 'user-table-body',
  summaryId = 'pagination-summary',
  currentUserRole = 'viewer'
} = {}) {
  const tableBody = document.getElementById(tableBodyId);
  const summary = document.getElementById(summaryId);
  const prevBtn = document.getElementById('prev-page');
  const nextBtn = document.getElementById('next-page');

  let currentPage = 1;
  const USERS_PER_PAGE = 10;

  async function loadUsers() {
    const offset = (currentPage - 1) * USERS_PER_PAGE;

    try {
      console.log(`Loading users with limit=${USERS_PER_PAGE}, offset=${offset}`);
      const response = await fetchUsers(USERS_PER_PAGE, offset);

      if (!response || !response.users) {
        throw new Error('Invalid response format');
      }

      renderUserRows(response.users);

      const start = offset + 1;
      const end = offset + response.users.length;
      summary.textContent = `Showing ${start}–${end} of ${response.total} users`;

      updatePaginationControls(response.total);
    } catch (err) {
      console.error('Error loading users:', err);
      summary.textContent = 'Failed to load users.';
    }
  }

  function updatePaginationControls(total) {
    const totalPages = Math.ceil(total / USERS_PER_PAGE);
    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages;
  }

  prevBtn.addEventListener('click', () => {
    if (currentPage > 1) {
      currentPage--;
      loadUsers();
    }
  });

  nextBtn.addEventListener('click', () => {
    currentPage++;
    loadUsers();
  });

  function renderUserRows(users) {
    tableBody.innerHTML = '';
    users.forEach((user, index) => {
      const role = user.roles?.[0] || 'viewer';
      const roleColor = role === 'admin'
        ? 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
        : role === 'editor'
        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
        : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100';

      const row = document.createElement('tr');
      row.className = "border-b border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800";
      row.innerHTML = `
        <td class="px-6 py-3">${index + 1 + (currentPage - 1) * USERS_PER_PAGE}</td>
        <td class="px-6 py-3 font-medium">${user.username}</td>
        <td class="px-6 py-3">${user.email}</td>
        <td class="px-6 py-3">
          <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full ${roleColor}">
            ${role}
          </span>
        </td>
        <td class="px-6 py-3">
          ${user.is_active
            ? `<span class="inline-flex items-center gap-1 text-green-600 dark:text-green-400 text-xs font-semibold">
                 <i data-lucide="check-circle" class="w-4 h-4"></i> Active
               </span>`
            : `<span class="inline-flex items-center gap-1 text-red-600 dark:text-red-400 text-xs font-semibold">
                 <i data-lucide="x-circle" class="w-4 h-4"></i> Inactive
               </span>`}
        </td>
        <td class="px-6 py-3 text-right">
          <a href="/dcp/admin/users/${user.id}/edit"
             class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 text-sm font-medium mr-4">
            Edit
          </a>
          ${(currentUserRole === 'admin' || currentUserRole === 'root') ? `
          <button data-user-id="${user.id}"
                  class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 text-sm font-medium delete-user-btn">
            Delete
          </button>` : ''}
        </td>`;
      tableBody.appendChild(row);
    });

    // Only create icons if lucide is available
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
          // When using the UMD bundle, the 'icons' object is usually
          // directly accessible as a property of the global 'lucide' object.
          lucide.createIcons({ icons: lucide.icons });
          // Or, if you want to apply to all elements with data-lucide attribute:
          // lucide.createIcons(); // This implicitly uses lucide.icons by default in UMD
      } else {
          console.error("Lucide library not found or not initialized correctly.");
      }
  }

  tableBody.addEventListener('click', async (e) => {
    if (e.target.classList.contains('delete-user-btn')) {
      const id = e.target.getAttribute('data-user-id');
      if (confirm('Are you sure you want to delete this user?')) {
        try {
          await deleteUser(id);
          await loadUsers();
        } catch {
          alert('Failed to delete user.');
        }
      }
    }
  });

  loadUsers();

  return {
    reload: loadUsers
  };
}
