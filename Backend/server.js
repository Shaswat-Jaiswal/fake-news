import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import connectDB from "./config/db.js";
import authRoutes from "./routes/authRoutes.js";
import newsRoutes from "./routes/newsRoutes.js";

dotenv.config();

console.log("JWT_SECRET:", process.env.JWT_SECRET);
console.log("MONGO_URI:", process.env.MONGO_URI);
console.log("✅ GUARDIAN_API_KEY:", process.env.GUARDIAN_API_KEY ? "Set" : "⚠️ Not set");

connectDB();

const app = express();

app.use(cors({
  origin: ["http://localhost:3000", 
    "http://localhost:5174", 
    "http://localhost:5173", 
    "https://fake-news-liart.vercel.app"
  ],
  methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"], // Explicitly allow methods
  allowedHeaders: ["Content-Type", "Authorization"], // Explicitly allow headers
  credentials: true,
}));


app.use(express.json());

app.get("/", (req, res) => {
  res.status(200).send("Server is live and running! 🚀");
});

// routes
app.use("/api/auth", authRoutes);
app.use("/api/news", newsRoutes);

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});