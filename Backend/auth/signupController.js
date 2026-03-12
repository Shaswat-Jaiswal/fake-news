import { User } from "../models/User.js";
import jwt from "jsonwebtoken";

export const signup = async (req, res) => {

  console.log("signup request body", req.body);

  const { firstName, lastName, email, username, password } = req.body;

  if (!firstName || !lastName || !email || !username || !password) {
    return res.status(400).json({ message: "Missing required fields" });
  }

  try {

    const existingUser = await User.findOne({
      $or: [{ email }, { username }]
    });

    if (existingUser) {
      return res.status(400).json({
        message: "Email or Username already exists"
      });
    }

    const user = new User({
      firstName,
      lastName,
      email,
      username,
      password
    });

    await user.save();

    const token = jwt.sign(
      { id: user._id },
      process.env.JWT_SECRET,
      { expiresIn: "1d" }
    );

    return res.status(201).json({
      message: "Signup Successful",
      token,
      user: {
        id: user._id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        username: user.username
      }
    });

  } catch (error) {

    console.error("Signup error:", error);

    if (error.code === 11000) {
      return res.status(400).json({ message: "Email or Username already registered" });
    }

    if (error.name === "ValidationError") {
      return res.status(400).json({ message: error.message });
    }

    return res.status(500).json({
      message: "Signup failed",
      error: error.message
    });
  }
};