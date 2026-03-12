import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Home } from "./Fake/Home/Home.jsx";
import { Signin } from "./Fake/Sign/Signin.jsx";
import { Login } from "./Fake/Log/Login.jsx";
import { ProtectedRoute } from "./Fake/utils/ProtectedRoute.jsx";

export const App = () => {
  return (
    <BrowserRouter>
      <Routes>
         <Route path="/" element={<Navigate to="/Home" />} />
        <Route path="/signin" element={<Signin />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/home"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
};
