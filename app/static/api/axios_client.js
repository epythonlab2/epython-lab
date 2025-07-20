// static/api/axios_client.js
import axios from "https://cdn.jsdelivr.net/npm/axios@1.4.0/+esm";

const client = axios.create({
  baseURL: "/api/v1/",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json"
  },
  withCredentials: true  // Required to send/receive cookies
});

// 🔐 Inject JWT from localStorage
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});


export default client;
