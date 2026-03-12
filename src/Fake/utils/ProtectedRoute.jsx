import { Navigate } from "react-router-dom";
import { isAuthenticated } from "./isAuthenticated.js";

export const ProtectedRoute = ({ children }) => {
  return isAuthenticated() ? children : <Navigate to="/login" />;
};
