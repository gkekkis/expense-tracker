// src/auth.js
export const USER_ID_KEY = "userId";

export function getUserId() {
  return localStorage.getItem(USER_ID_KEY);
}

export function setUserId(userId) {
  localStorage.setItem(USER_ID_KEY, userId);
}

export function clearUserId() {
  localStorage.removeItem(USER_ID_KEY);
}

// Simple UUID validation (good enough for MVP)
export function isUuid(value) {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
    value.trim()
  );
}
