import axios from "axios";

export const api = axios.create({
  baseURL: "/api", // uses Vite proxy to backend
});

api.interceptors.request.use((config) => {
  const currentUserId = localStorage.getItem("current_user_id");
  if (currentUserId) {
    // your backend uses query param current_user_id, so we attach it automatically
    config.params = { ...(config.params || {}), current_user_id: currentUserId };
  }
  return config;
});
