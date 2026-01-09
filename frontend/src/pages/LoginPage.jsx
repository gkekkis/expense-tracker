// src/pages/LoginPage.jsx
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { isUuid, setUserId } from "../auth";

export default function LoginPage() {

  const navigate = useNavigate();
  const [value, setValue] = useState("");
  const [touched, setTouched] = useState(false);

  const trimmed = value.trim();
  const valid = useMemo(() => isUuid(trimmed), [trimmed]);

  function onSubmit(e) {
    e.preventDefault();
    setTouched(true);
    if (!valid) return;

    setUserId(trimmed);
    navigate("/", { replace: true });
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.h1}>Select user</h1>
        <p style={styles.p}>
          Dev-only identity stub. Enter a user UUID to call the API.
        </p>

        <form onSubmit={onSubmit} style={styles.form}>
          <label style={styles.label}>
            User UUID
            <input
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onBlur={() => setTouched(true)}
              placeholder="e.g. 2f1c9b1e-7c2b-4f9e-9d6e-4a7d5d2c1a0b"
              style={styles.input}
              autoFocus
            />
          </label>

          {touched && !valid && (
            <div style={styles.error}>Please enter a valid UUID.</div>
          )}

          <button type="submit" style={styles.button} disabled={!trimmed}>
            Continue
          </button>
        </form>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "grid",
    placeItems: "center",
    padding: 24,
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif",
  },
  card: {
    width: "min(520px, 100%)",
    border: "1px solid #e5e7eb",
    borderRadius: 16,
    padding: 20,
    boxShadow: "0 8px 24px rgba(0,0,0,0.06)",
  },
  h1: { margin: 0, fontSize: 22 },
  p: { marginTop: 8, marginBottom: 16, color: "#555" },
  form: { display: "grid", gap: 12 },
  label: { display: "grid", gap: 6, fontSize: 14 },
  input: {
    padding: "10px 12px",
    borderRadius: 10,
    border: "1px solid #d1d5db",
    fontSize: 14,
  },
  error: { color: "#b91c1c", fontSize: 13 },
  button: {
    padding: "10px 12px",
    borderRadius: 10,
    border: "1px solid #111827",
    background: "#111827",
    color: "white",
    fontSize: 14,
    cursor: "pointer",
  },
};
