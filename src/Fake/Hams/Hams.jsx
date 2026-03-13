import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Hams.css";

export const Hams = () => {
   const[menuOpen, setMenuOpen] = useState(false);
   const navigate = useNavigate();

   const handleLogout = () => {
      localStorage.removeItem("token");
      navigate("/");
      setMenuOpen(false);
   };


    return(
       <div className="A">
        <div className="hamsburger" onClick={()=>setMenuOpen(!menuOpen)}>
         <span className="line1"></span>
         <span className="line2"></span>
         <span className="line3"></span>
        </div>

         {menuOpen && (
            <div className="hamsburger-menu">
                <div className="Login">
                     <h2 className="login-title">Welcome</h2>
                      <p className="login-btn">
                        <span
                        style={{ cursor: "pointer"}}
                        onClick={() => {navigate("/signin"); setMenuOpen(false);}}
                        >Signin
                        </span>
                        {" / "}
                        <span
                        style={{ cursor: "pointer"}}
                        onClick={() => {navigate("/login"); setMenuOpen(false);}}
                        >Login</span>
                      </p>
                      <span
              className="log"
              style={{ cursor: "pointer" }}
              onClick={handleLogout}
            >
              Logout
            </span>
                </div>
                </div>
        )} 
        </div>
    )
}