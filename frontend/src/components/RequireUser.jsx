import { Navigate, Outlet } from "react-router-dom";
import { getUserId } from "../auth";

export function RequireUser() {
  const userId = getUserId();
  if (!userId) return <Navigate to="/login" replace />;
  return <Outlet />;
}
