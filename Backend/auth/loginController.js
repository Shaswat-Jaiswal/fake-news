import { User } from "../models/User.js";
import jwt from "jsonwebtoken";

export const login = async (req, res) => {
   console.log("LOGIN BODY:", req.body);


  const { email, username, password } = req.body;

  if ((!email && !username) || !password) {
    return res.status(400).json({
      message: "Email/Username and password are required"
    });
  }

  try {

    // user search by email OR username
    const user = await User.findOne({
      $or: [
        { email: email?.toLowerCase() },
        { username: username }
      ]
    });

    if (!user) {
      return res.status(400).json({
        message: "Invalid credentials"
      });
    }

    const isMatch = await user.comparePassword(password);

    if (!isMatch) {
      return res.status(400).json({
        message: "Invalid credentials"
      });
    }

    const token = jwt.sign(
      { id: user._id },
      process.env.JWT_SECRET,
      { expiresIn: "1d" }
    );

    res.json({
      message: "Login successful",
      token,
      user: {
        id: user._id,
        firstName: user.firstName,
        lastName: user.lastName,
        username: user.username,   // ✅ added
        email: user.email
      }
    });

  } catch (error) {

    console.error("Login error:", error);

    res.status(500).json({
      message: "Login failed",
      error: error.message
    });
  }
};
