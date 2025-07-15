// static/auth/login.js
import auth_client from "./auth_client.js";

export async function loginUser({ username, password }) {
  const res = await auth_client.post("/login", { username, password }, {
    withCredentials: true  // Important: allows cookie to be set
  });

  // Redirect to protected route
  window.location.href = "/dcp/dashboard";
}
