// static/api/user_management.js
import auth_client from "./auth_client.js";

// Fetch all users (optionally with filters or pagination)
// Fetch all users with optional filters or pagination
export async function fetchUsers(limit = 10, offset = 0, filters = {}) {
  // Construct the query string based on the provided filters
  const { search = '', role = '', status = '' } = filters;

  const res = await auth_client.get('/users', {
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
  const res = await auth_client.get(`/users/${userId}`);
  return res.data;
}

// Create a new user
export async function createUser(userData) {
  const res = await auth_client.post("/users/create", userData);
  return res.data;
}

// Update an existing user
export async function updateUser(userId, userData) {
  const res = await auth_client.put(`/users/${userId}`, userData);
  return res.data;
}

// Delete a user
export async function deleteUser(userId) {
  const res = await auth_client.delete(`/users/${userId}`);
  return res.data;
}
