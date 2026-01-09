// src/pages/ExpensesPage.jsx
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { createExpense, listAllExpenses } from "../api.js";
import { Modal } from "../components/Modal";

const CATEGORIES = [
  "Rental",
  "Bills",
  "Groceries",
  "Household",
  "Delivery Food",
  "Dining Out",
  "Pet",
  "Gas",
  "Car",
  "Travel",
  "Entertainment",
  "Health",
  "Personal",
  "Savings",
  "Miscellaneous",
];

function todayISO() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

export default function ExpensesPage() {
  const { accountId } = useParams();
  const navigate = useNavigate();

  const [allExpenses, setAllExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const expenses = useMemo(() => {
    return allExpenses
      .filter((e) => e.account_id === accountId)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  }, [allExpenses, accountId]);

  const [showCreate, setShowCreate] = useState(false);
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("Miscellaneous");
  const [expenseDate, setExpenseDate] = useState(todayISO());

  const validAmount = useMemo(() => Number(amount) > 0, [amount]);

  async function refresh() {
    setLoading(true);
    setErr("");
    try {
      const data = await listAllExpenses();
      setAllExpenses(Array.isArray(data) ? data : []);
    } catch (e) {
      setErr(e.message || "Failed to load expenses");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, [accountId]);

  function openCreate() {
    setErr("");
    setAmount("");
    setDescription("");
    setCategory("Miscellaneous");
    setExpenseDate(todayISO());
    setShowCreate(true);
  }

  async function onCreate(e) {
    e.preventDefault();
    if (!validAmount) return;

    try {
      await createExpense({
        account_id: accountId,
        amount: Number(amount),
        description: description.trim() || "", // keep it a string
        category, // must match enum strings exactly
        expense_date: expenseDate, // YYYY-MM-DD
      });

      setShowCreate(false);
      await refresh();
    } catch (e2) {
      setErr(e2.message || "Failed to create expense");
    }
  }

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <button style={styles.back} onClick={() => navigate("/")}>
          ← Back
        </button>

        <div>
          <h1 style={styles.h1}>Expenses</h1>
          <div style={styles.sub}>
            Account: <code>{accountId}</code>
          </div>
        </div>

        <button style={styles.btn} onClick={openCreate}>
          + Add expense
        </button>
      </header>

      {err && <div style={styles.error}>{err}</div>}

      {loading ? (
        <div style={styles.muted}>Loading…</div>
      ) : expenses.length === 0 ? (
        <div style={styles.empty}>No expenses yet.</div>
      ) : (
        <div style={styles.list}>
          {expenses.map((e) => (
            <div key={e.id} style={styles.card}>
              <div style={styles.topRow}>
                <div style={styles.amount}>€{e.amount}</div>
                <div style={styles.badge}>{e.category}</div>
              </div>
              <div style={styles.desc}>{e.description || "(no description)"}</div>
              <div style={styles.meta}>
                Date:{" "}
                <strong>
                  {e.expense_date
                    ? new Date(e.expense_date).toLocaleDateString()
                    : "-"}
                </strong>
                {" · "}
                Created:{" "}
                {e.created_at ? new Date(e.created_at).toLocaleString() : ""}
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <Modal title="Add expense" onClose={() => setShowCreate(false)}>
          <form onSubmit={onCreate} style={{ display: "grid", gap: 10 }}>
            <label style={styles.label}>
              Amount (€)
              <input
                type="number"
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                style={styles.input}
                autoFocus
              />
            </label>

            <label style={styles.label}>
              Category
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                style={styles.input}
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>

            <label style={styles.label}>
              Expense date
              <input
                type="date"
                value={expenseDate}
                onChange={(e) => setExpenseDate(e.target.value)}
                style={styles.input}
              />
            </label>

            <label style={styles.label}>
              Description
              <input
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Optional"
                style={styles.input}
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
              <button type="submit" style={styles.btn} disabled={!validAmount}>
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
  header: { display: "flex", alignItems: "flex-start", gap: 12, marginBottom: 16 },
  back: {
    border: "1px solid #e5e7eb",
    background: "white",
    borderRadius: 10,
    padding: "8px 10px",
    cursor: "pointer",
  },
  h1: { margin: 0, fontSize: 22 },
  sub: { marginTop: 6, color: "#555", fontSize: 13 },
  btn: {
    marginLeft: "auto",
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
    color: "#555",
    maxWidth: 520,
  },
  list: { display: "grid", gap: 10 },
  card: { border: "1px solid #e5e7eb", borderRadius: 14, padding: 12, display: "grid", gap: 6 },
  topRow: { display: "flex", justifyContent: "space-between", gap: 10 },
  amount: { fontWeight: 800 },
  badge: {
    fontSize: 12,
    border: "1px solid #e5e7eb",
    borderRadius: 999,
    padding: "2px 8px",
    background: "white",
  },
  desc: { color: "#111827" },
  meta: { color: "#555", fontSize: 12 },
  label: { display: "grid", gap: 6, fontSize: 14 },
  input: {
    padding: "10px 12px",
    borderRadius: 10,
    border: "1px solid #d1d5db",
    fontSize: 14,
    background: "white",
  },
};
