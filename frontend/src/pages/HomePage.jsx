// src/pages/HomePage.jsx
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { clearUserId, getUserId } from "../auth";
import { createAccount, listAccounts } from "../api";
import { Modal } from "../components/Modal";

export default function HomePage() {
  const userId = getUserId();
  const navigate = useNavigate();

  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const canCreate = useMemo(() => newName.trim().length >= 2, [newName]);

  async function refresh() {
    setLoading(true);
    setErr("");
    try {
      const data = await listAccounts();
      setAccounts(Array.isArray(data) ? data : []);
    } catch (e) {
      setErr(e.message || "Failed to load accounts");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function onCreate(e) {
    e.preventDefault();
    setErr("");
    if (!canCreate) return;

    try {
      await createAccount(newName.trim());
      setShowCreate(false);
      setNewName("");
      await refresh();
    } catch (e2) {
      setErr(e2.message || "Failed to create account");
    }
  }

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.h1}>Accounts</h1>
          <div style={styles.sub}>
            User: <code>{userId}</code>
          </div>
        </div>

        <div style={styles.headerActions}>
          <button style={styles.btn} onClick={() => setShowCreate(true)}>
            + Create account
          </button>
          <button
            style={styles.btnSecondary}
            onClick={() => {
              clearUserId();
              window.location.href = "/login";
            }}
          >
            Log out
          </button>
        </div>
      </header>

      {err && <div style={styles.error}>{err}</div>}

      {loading ? (
        <div style={styles.muted}>Loading…</div>
      ) : accounts.length === 0 ? (
        <div style={styles.empty}>
          <p style={{ marginTop: 0 }}>
            No accounts yet. Create your first account.
          </p>
          <button style={styles.btn} onClick={() => setShowCreate(true)}>
            + Create account
          </button>
        </div>
      ) : (
        <div style={styles.grid}>
          {accounts.map((a) => (
            <div key={a.id} style={styles.card}>
              <div style={styles.cardTitle}>{a.name}</div>
              <div style={styles.cardMeta}>
                <div>
                  <span style={styles.metaLabel}>ID:</span> <code>{a.id}</code>
                </div>
                {a.status && (
                  <div>
                    <span style={styles.metaLabel}>Status:</span> {a.status}
                  </div>
                )}
              </div>

              <button
                style={styles.btnSecondary}
                onClick={() => navigate(`/accounts/${a.id}`)}
              >
                Open
              </button>
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <Modal title="Create account" onClose={() => setShowCreate(false)}>
          <form onSubmit={onCreate} style={{ display: "grid", gap: 10 }}>
            <label style={styles.label}>
              Account name
              <input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="e.g. Personal, Family, Trip to Japan…"
                style={styles.input}
                autoFocus
              />
            </label>
            <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
              <button
                type="button"
                style={styles.btnSecondary}
                onClick={() => setShowCreate(false)}
              >
                Cancel
              </button>
              <button type="submit" style={styles.btn} disabled={!canCreate}>
                Create
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}

const styles = {
  page: {
    padding: 24,
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif",
  },
  header: {
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "space-between",
    gap: 16,
    marginBottom: 16,
  },
  h1: { margin: 0, fontSize: 24 },
  sub: { marginTop: 6, color: "#555", fontSize: 13 },
  headerActions: { display: "flex", gap: 10, flexWrap: "wrap" },
  btn: {
    border: "1px solid #111827",
    background: "#111827",
    color: "white",
    padding: "10px 12px",
    borderRadius: 10,
    cursor: "pointer",
  },
  btnSecondary: {
    border: "1px solid #e5e7eb",
    background: "white",
    color: "#111827",
    padding: "10px 12px",
    borderRadius: 10,
    cursor: "pointer",
  },
  error: {
    background: "#fee2e2",
    border: "1px solid #fecaca",
    color: "#7f1d1d",
    padding: 12,
    borderRadius: 12,
    marginBottom: 12,
  },
  muted: { color: "#555" },
  empty: {
    border: "1px dashed #d1d5db",
    borderRadius: 16,
    padding: 16,
    display: "grid",
    gap: 10,
    maxWidth: 520,
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
    gap: 12,
    marginTop: 12,
  },
  card: {
    border: "1px solid #e5e7eb",
    borderRadius: 16,
    padding: 14,
    display: "grid",
    gap: 10,
  },
  cardTitle: { fontSize: 16, fontWeight: 700 },
  cardMeta: { color: "#555", fontSize: 13, display: "grid", gap: 6 },
  metaLabel: { color: "#111827", fontWeight: 600 },
  label: { display: "grid", gap: 6, fontSize: 14 },
  input: {
    padding: "10px 12px",
    borderRadius: 10,
    border: "1px solid #d1d5db",
    fontSize: 14,
  },
};
