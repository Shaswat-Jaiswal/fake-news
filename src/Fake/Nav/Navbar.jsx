import { useNavigate } from "react-router-dom";
import { useState } from "react";
import './Navbar.css';


export const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
    return(
        <div className="navbar"> 
         <div className="nav-left">
          <div></div>
          <div></div>
          <div></div>
         </div>
        
         <div className="nav-right">
        <h2 className="nav-item" onClick={() => navigate("/home")}> Home </h2>
        <h2 className="nav-item"> About </h2>
        <h2 className="nav-item"> Blog </h2>
        <h2 className="nav-item"> Setting </h2>
        </div>
        </div>
    )
}

export default Navbar;