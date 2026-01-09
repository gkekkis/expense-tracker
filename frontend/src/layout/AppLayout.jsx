import { Link, Outlet, useNavigate } from "react-router-dom";

export default function AppLayout() {
  const navigate = useNavigate();
  const currentUserId = localStorage.getItem("current_user_id");

  const logout = () => {
    localStorage.removeItem("current_user_id");
    navigate("/login");
  };

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: 16, fontFamily: "system-ui" }}>
      <header style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 16 }}>
        <Link to="/accounts" style={{ textDecoration: "none", fontWeight: 700 }}>Expense Tracker</Link>

        <div style={{ marginLeft: "auto", display: "flex", gap: 12, alignItems: "center" }}>
          <span style={{ opacity: 0.7, fontSize: 14 }}>
            {currentUserId ? `current_user_id: ${currentUserId}` : "Not logged in"}
          </span>
          {currentUserId ? (
            <button onClick={logout}>Logout</button>
          ) : (
            <button onClick={() => navigate("/login")}>Login</button>
          )}
        </div>
      </header>

      <Outlet />
    </div>
  );
}
