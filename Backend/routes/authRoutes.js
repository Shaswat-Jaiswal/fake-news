import express from "express";
import { signup } from "../auth/signupController.js";
import { login } from "../auth/loginController.js";
import { authMiddleware } from "../middleware/authMiddleware.js";

const router = express.Router();

//Public routes
router.post("/signup", signup);
router.post("/login", login);

// 🔒 Protected Route (example)
router.get("/profile", authMiddleware, (req, res) => {
  res.json({
    message: "Protected profile route",
    user: req.user, // middleware se aaya hua user
  });
});

export default router;