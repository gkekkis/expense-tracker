import { useParams } from "react-router-dom";
import Expenses from "./Expenses.jsx";
import Members from "./Members.jsx";
import { useState } from "react";

export default function AccountDetails() {
  const { accountId } = useParams();
  const [tab, setTab] = useState("expenses");

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Account</h2>
      <div style={{ fontSize: 13, opacity: 0.7, marginBottom: 12 }}>id: {accountId}</div>

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button onClick={() => setTab("expenses")} disabled={tab === "expenses"}>Expenses</button>
        <button onClick={() => setTab("members")} disabled={tab === "members"}>Members</button>
      </div>

      {tab === "expenses" ? <Expenses accountId={accountId} /> : <Members accountId={accountId} />}
    </div>
  );
}
