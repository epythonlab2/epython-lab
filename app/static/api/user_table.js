import { fetchUsers, deleteUser, getUserById, updateUser } from '/static/api/user_api.js';

export function initUserTable({
  tableBodyId = 'user-table-body',
  summaryId = 'pagination-summary',
  currentUserRole = 'viewer'
} = {}) {
  const tableBody = document.getElementById(tableBodyId);
  const summary = document.getElementById(summaryId);
  const prevBtn = document.getElementById('prev-page');
  const nextBtn = document.getElementById('next-page');

  const searchInput = document.getElementById('search-input');
  const roleFilter = document.getElementById('role-filter');
  const statusFilter = document.getElementById('status-filter');

  let currentPage = 1;
  const USERS_PER_PAGE = 10;
  let filters = {
    search: '',
    role: '',
    status: ''
  };

  // Load users from API with filters
  async function loadUsers() {
    const offset = (currentPage - 1) * USERS_PER_PAGE;
    try {
      const response = await fetchUsers(USERS_PER_PAGE, offset, filters);

      if (!response || !response.users) {
        throw new Error('Invalid response format or no users returned.');
      }

      renderUserRows(response.users);

      const start = offset + 1;
      const end = offset + response.users.length;
      summary.textContent = `Showing ${start}–${end} of ${response.total} users`;

      updatePaginationControls(response.total);
    } catch (err) {
      console.error('Error loading users:', err);
      summary.textContent = 'Failed to load users.';
      showToast('❌ Failed to load users.', 'error');
    }
  }

  // Update pagination controls based on total number of users
  function updatePaginationControls(total) {
    const totalPages = Math.ceil(total / USERS_PER_PAGE);
    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages;
  }

  // Event listeners for pagination buttons
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

  // Event listeners for filter inputs
  searchInput.addEventListener('input', (e) => {
    filters.search = e.target.value.trim();
    loadUsers();
  });

  roleFilter.addEventListener('change', (e) => {
    filters.role = e.target.value;
    loadUsers();
  });

  statusFilter.addEventListener('change', (e) => {
    filters.status = e.target.value;
    loadUsers();
  });

  // Render user rows in the table
  function renderUserRows(users) {
    tableBody.innerHTML = '';  // Clear the existing rows

    users.forEach((user, index) => {
      const role = user.roles?.[0] || 'viewer';
      const roleColor = getRoleColor(role);

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
          <a href="#"
             class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 text-sm font-medium mr-4 edit-user-btn"
             data-user-id="${user.id}">
            Edit
          </a>
          ${(currentUserRole === 'admin' || currentUserRole === 'root') && !user.roles.includes('admin') && !user.roles.includes('root') ? `
          <button data-user-id="${user.id}"
                  class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 text-sm font-medium delete-user-btn">
            Delete
          </button>` : ''}
        </td>`;
      tableBody.appendChild(row);
    });

    // Create icons only once if lucide is available
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
      lucide.createIcons({ icons: lucide.icons });
    } else {
      console.error("Lucide library not found or not initialized correctly.");
    }
  }

  // Get role color based on user role
  function getRoleColor(role) {
    switch (role) {
      case 'admin':
        return 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100';
      case 'editor':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100';
    }
  }

  // Show toast notifications
  function showToast(message, type = 'info') {
    const colors = {
      success: '#16a34a',  // green
      error: '#dc2626',    // red
      warning: '#f59e0b',  // yellow
      info: '#3b82f6'      // blue
    };

    Toastify({
      text: message,
      duration: 4000,
      gravity: 'top',
      position: 'right',
      background: colors[type] || colors.info,
      close: true
    }).showToast();
  }

  // Handle delete user action
  tableBody.addEventListener('click', async (e) => {
    if (e.target.classList.contains('delete-user-btn')) {
      const id = e.target.getAttribute('data-user-id');
      if (confirm('Are you sure you want to delete this user?')) {
        const deleteButton = e.target;
        deleteButton.innerHTML = '<i class="w-4 h-4 animate-spin" data-lucide="loader"></i> Deleting...';
        deleteButton.disabled = true;

        try {
          await deleteUser(id);
          showToast('✅ User deleted successfully', 'success'); // Success toast

          // Reload users after deletion
          await loadUsers();  // Reload users after deletion
        } catch (err) {
          showToast('❌ Failed to delete user.', 'error'); // Error toast
        } finally {
          // Restore button text and re-enable it
          deleteButton.innerHTML = 'Delete';
          deleteButton.disabled = false;
        }
      }
    }
    if (e.target.classList.contains('edit-user-btn')) {
      const userId = e.target.getAttribute('data-user-id');
      openEditUserModal(userId);  // Open the Edit Modal
    }
  });

  // Open Edit User Modal
  async function openEditUserModal(userId) {
    const modal = document.getElementById('edit-user-modal');
    const user = await getUserById(userId);

    document.getElementById('edit-user-id').value = user.id;
    document.getElementById('edit-username').value = user.username;
    document.getElementById('edit-email').value = user.email;
    document.getElementById('edit-role').value = user.roles[0];
    document.getElementById('edit-status').value = user.is_active ? 'active' : 'inactive';

    modal.classList.remove('hidden');
  }

  // Handle the Edit User Form Submit
  document.getElementById('edit-user-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const userId = document.getElementById('edit-user-id').value;

    const updatedUser = {
      username: formData.get('username'),
      email: formData.get('email'),
      is_active: formData.get('status') === 'active',
      // Pass the role only when allowed (root or user with permission)
      roles: currentUserRole === 'admin' || currentUserRole === 'root'
        ? [formData.get('role')]  // Pass the role only if currentUser is root
        : undefined               // Admin cannot change roles
    };

    try {
      await updateUser(userId, updatedUser);
      showToast('✅ User updated successfully', 'success');
      loadUsers();  // Reload the user list
      document.getElementById('edit-user-modal').classList.add('hidden');  // Hide the modal
    } catch (err) {
      showToast('❌ Failed to update user.', 'error');
    }

  });

  loadUsers();  // Initial loading of users

  return {
    reload: loadUsers
  };
}
