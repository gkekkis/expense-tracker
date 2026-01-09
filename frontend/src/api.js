// src/api.js
import { getUserId } from "./auth";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

function formatErrorDetail(detail) {
  // FastAPI validation errors: detail is often an array
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        const loc = Array.isArray(d.loc) ? d.loc.join(".") : "";
        const msg = d.msg || "Invalid value";
        return loc ? `${loc}: ${msg}` : msg;
      })
      .join(" | ");
  }
  if (typeof detail === "string") return detail;
  return "Request failed";
}

async function request(path, options = {}) {
  const userId = getUserId();
  if (!userId) throw new Error("Missing user id");

  const headers = new Headers(options.headers);
  headers.set("X-User-Id", userId);

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  const contentType = res.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await res.json() : await res.text();

  if (!res.ok) {
    const detail =
      payload && typeof payload === "object" && payload.detail
        ? formatErrorDetail(payload.detail)
        : `Request failed (${res.status})`;

    const error = new Error(detail);
    error.status = res.status;
    error.payload = payload;
    throw error;
  }

  return payload;
}

export function listAccounts() {
  return request("/api/v1/accounts");
}

export function createAccount(name) {
  return request("/api/v1/accounts", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export function listAllExpenses() {
  return request("/api/v1/expenses");
}

export function createExpense(payload) {
  return request("/api/v1/expenses", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
