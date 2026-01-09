import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../services/api.js";

export default function Accounts() {
  const [accounts, setAccounts] = useState([]);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const currentUserId = localStorage.getItem("current_user_id");
    if (!currentUserId) {
      navigate("/login");
      return;
    }

    (async () => {
      try {
        setErr("");
        setLoading(true);
        // NOTE: adjust endpoint if yours differs
        const res = await api.get("/v1/accounts");
        setAccounts(res.data);
      } catch (e) {
        setErr(e?.response?.data?.detail || e.message || "Failed to load accounts");
      } finally {
        setLoading(false);
      }
    })();
  }, [navigate]);

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Accounts</h2>

      {loading && <p>Loading...</p>}
      {err && <p style={{ color: "crimson" }}>{err}</p>}

      {!loading && !err && (
        <div style={{ display: "grid", gap: 10 }}>
          {accounts.map((a) => (
            <Link
              key={a.id}
              to={`/accounts/${a.id}`}
              style={{
                padding: 12,
                border: "1px solid #ddd",
                borderRadius: 12,
                textDecoration: "none",
                color: "inherit",
              }}
            >
              <div style={{ fontWeight: 700 }}>{a.name}</div>
              <div style={{ fontSize: 13, opacity: 0.7 }}>
                status: {a.status} • id: {a.id}
              </div>
            </Link>
          ))}
          {accounts.length === 0 && <p style={{ opacity: 0.7 }}>No accounts found.</p>}
        </div>
      )}
    </div>
  );
}
