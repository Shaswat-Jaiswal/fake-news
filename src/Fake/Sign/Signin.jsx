import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { signupUser } from "../api/authApi";
import "./Signin.css";

export const Signin = () => {
       const[firstName, setFirstName] = useState("");
       const[lastName, setLastName] = useState("");
       const[email, setEmail] = useState("");
       const[username, setUserName] = useState("");
       const [password, setPassword] = useState("");
       const [confirmPassword, setConfirmPassword] = useState("");
       const [animationType, setAnimationType] = useState("");
       const navigate = useNavigate();

       const handleSignup = async () => {
        if(!firstName || !lastName || !email || !username || !password || !confirmPassword){
          alert("Please fill in all fileds ");
          return;
        }
         if (password !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }
    try {
      const res = await signupUser({
        firstName,
        lastName,
        email,
        username,
        password,
      });

      localStorage.setItem("token", res.data.token);
      alert("Signup successful");
      navigate("/login");
    } catch (error) {
      console.error("Signup error:", error);
      const msg =
        error.response?.data?.message ||
        error.response?.data?.error ||
        error.message ||
        "Signup failed";
      alert(msg);
    }
       }

      useEffect(() => {
    const animations = ["bubble", "square", "particle", "wave"];
    const random = animations[Math.floor(Math.random() * animations.length)];
    setAnimationType(random);
  }, []);


    return(
        <div className="signin-container">
      <div className="background">

        {animationType === "bubble" && (
          <>
            <div className="bubble"></div>
            <div className="bubble"></div>
             <div className="bubble"></div>
          </>
        )}

        {animationType === "square" && (
          <>
            <div className="square"></div>
            <div className="square"></div>
             <div className="square"></div>
          </>
        )}

        {animationType === "particle" && (
          <>
            <div className="particle"></div>
            <div className="particle"></div>
             <div className="particle"></div>
          </>
        )}

        {animationType === "wave" && (
          <>
            <div className="wave"></div>
            <div className="wave"></div>
            <div className="wave"></div>
          </>
        )}

      </div>

      
      <div className="Signin-card">
        <h2>Sign in</h2>
       
       
        <div className="form-grid">
            
          <input
            type="text"
            placeholder="First Name"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
          />

          <input
            type="text"
            placeholder="Last Name"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
          />

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            type="Username"
            placeholder="Username"
            value={username}
            onChange={(e) => setUserName(e.target.value)}
          />
            
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
           
          <input
            type="password"
            placeholder="Confirm Password"
            className="full"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        </div>

        <button type="submit" onClick={handleSignup}>Sign up</button>

        <p className="signup-text">
     Already have an account?  <Link to="/login">Login</Link>
      </p>
      </div>

    </div>
  );
};
