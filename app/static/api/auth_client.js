// static/api/auth_client.js
import axios from "https://cdn.jsdelivr.net/npm/axios@1.4.0/+esm";

const auth_client = axios.create({
  baseURL: "/api/v1/auth",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json"
  },
  withCredentials: true  // Required to send/receive cookies
});

// 🔐 Inject JWT from localStorage
auth_client.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});


export default auth_client;
