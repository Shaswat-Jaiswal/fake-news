import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { loginUser } from "../api/authApi";
import "./Login.css";

export const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    if (!email || !password) {
  alert("Please enter email and password");
  return;
}
    try {
      const res = await loginUser({
        email,
        password,
      });

      localStorage.setItem("token", res.data.token);
      alert("Login successful");
      navigate("/home");
    } catch (error) {
      console.error("Login error:", error);
      const msg =
        error.response?.data?.message ||
        error.response?.data?.error ||
        error.message ||
        "Login failed";
      alert(msg);
    }
  };

  useEffect(() => {
    const sphere = document.querySelectorAll(".sphere");
    const intervals = [];

    sphere.forEach((sphere) => {
      const interval = setInterval(() => {
        sphere.style.top = Math.random() * 80 + "%";
        sphere.style.left = Math.random() * 80 + "%";
      }, 4000);

      intervals.push(interval);
    });

    return () => intervals.forEach(clearInterval);
  }, []);

  return (
    <div className="login-container">

      {/* Background */}
      <div className="background">
        <div className="sphere s1"></div>
        <div className="sphere s2"></div>
        <div className="sphere s3"></div>
      </div>

      {/* Signin Card */}
      <div className="login-card">
        <h2>LOGIN</h2>
       
       
        <div className="input-group">
            

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
            
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
           
        </div>

        <button type="submit" onClick={handleLogin}>Log in</button>

       <p className="login-text">
      New user? <Link to="/signin">Sign up</Link>
    </p>
      </div>

    </div>
  );
};