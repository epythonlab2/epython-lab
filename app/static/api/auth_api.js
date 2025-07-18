// static/auth/login.js
import client from "./axios_client.js";

export async function loginUser({ username, password }) {
  const res = await client.post("/auth/login", { username, password }, {
    withCredentials: true  // Important: allows cookie to be set
  });

  // Redirect to protected route
  window.location.href = "/dcp/dashboard";
}


// Fetch all users (optionally with filters or pagination)
// Fetch all users with optional filters or pagination
export async function fetchUsers(limit = 10, offset = 0, filters = {}) {
  // Construct the query string based on the provided filters
  const { search = '', role = '', status = '' } = filters;

  const res = await client.get('/auth/users', {
    params: {
      limit,
      offset,
      search,
      role,
      status
    }
  });

  return res.data;  // { total, users }
}


// Fetch a single user by ID
export async function getUserById(userId) {
  const res = await client.get(`/auth/users/${userId}`);
  return res.data;
}

// Create a new user
export async function createUser(userData) {
  const res = await client.post("/auth/users/create", userData);
  return res.data;
}

// Update an existing user
export async function updateUser(userId, userData) {
  const res = await client.put(`/auth/users/${userId}`, userData);
  return res.data;
}

// Delete a user
export async function deleteUser(userId) {
  const res = await client.delete(`/auth/users/${userId}`);
  return res.data;
}

// Get login history
export async function loginHistory(userId, page = 1, limit = 10, search = "") {
  const res = await client.get(`/audit/user-login-history/${userId}`, {
    params: { page, limit, search }
  });
  return res.data;
}
