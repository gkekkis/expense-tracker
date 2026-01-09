import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import LoginPage from "./pages/LoginPage.jsx";
import HomePage from "./pages/HomePage.jsx";
import ExpensesPage from "./pages/ExpensesPage.jsx";
import { RequireUser } from "./components/RequireUser.jsx";

const root = document.getElementById("root");

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        {/* public */}
        <Route path="/login" element={<LoginPage />} />

        {/* protected */}
        <Route element={<RequireUser />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/accounts/:accountId" element={<ExpensesPage />} />
        </Route>

        {/* fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
