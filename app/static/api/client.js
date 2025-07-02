// static/js/client.js
import axios from "https://cdn.jsdelivr.net/npm/axios@1.4.0/+esm";

const client = axios.create({
  baseURL: "/api/v1/topics", // Adjust if your API has a different base path
  timeout: 10000, // 10 seconds timeout (optional)
  headers: {
    "Content-Type": "application/json",
    // Add more headers here if needed, e.g. Authorization
  },
});

export default client;
