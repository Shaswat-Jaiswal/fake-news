import express from "express";
import axios from "axios";

const router = express.Router();

// 🔹 ML API Configuration
const ML_API_URL = process.env.ML_API_URL || "http://127.0.0.1:5001";

// 🔹 Guardian checker
const checkGuardian = async (text) => {
  const GUARDIAN_API_KEY = process.env.GUARDIAN_API_KEY;

  try {
    if (!GUARDIAN_API_KEY) {
      console.warn("⚠️ GUARDIAN_API_KEY not set");
      return { found: false, articles: [] };
    }

    const cleanText = text
      .toLowerCase()
      .replace(/[’'"]/g, "")
      .replace(/[^a-z0-9\s]/g, "");

    // 🔹 Better keyword extraction
    const stopWords = ["is","the","a","an","on","in","to","from","and","or","by","of","hasnt","despite"];
    const keywords = cleanText
      .split(/\s+/)
      .filter(w => w.length > 4 && !stopWords.includes(w))
      .slice(0, 6)
      .join(" ");


    console.log("🔍 Guardian search keywords:", keywords);

    const response = await axios.get(
      "https://content.guardianapis.com/search",
      {
        params: {
          q: keywords,
          "api-key": GUARDIAN_API_KEY,
          "page-size": 5,
          "order-by": "relevance"
        }
      }
    );

    const results = response.data?.response?.results || [];

    if (results.length > 0) {
      return {
        found: true,
        articles: results.map(a => ({
          title: a.webTitle,
          url: a.webUrl,
          publication: "The Guardian"
        }))
      };
    }

    return { found: false, articles: [] };

  } catch (err) {
    console.error("❌ Guardian API error:", err.message);
    return { found: false, articles: [] };
  }
};

// 🔹 Analyze route
router.post("/analyze", async (req, res) => {
  try {
    const { text } = req.body;

    if (!text || !text.trim()) {
      return res.status(400).json({ message: "Text is empty" });
    }

    // ML API
    const mlResponse = await axios.post(
      `${ML_API_URL}/check`,
      { text }
    );

  let result = "";

const prediction = mlResponse.data.prediction;
const confidence = mlResponse.data.confidence;

const sourceVerification = mlResponse.data.source_verification || [];

if (prediction === "Real") {
  result = `Real (Confidence: ${confidence}%)`;
} else {
  result = `Fake (Confidence: ${confidence}%)`;
}

    console.log("📰 Final result:", result);

    res.json({
      result,
      prediction: mlResponse.data.prediction,
      confidence: mlResponse.data.confidence,
      source_verification: sourceVerification,
      reason: mlResponse.data.reason,
      source: mlResponse.data.source
    });

  } catch (error) {
    console.error("ML ERROR ❌", error.message);
    res.status(500).json({ message: "ML analysis failed" });
  }
});

export default router;
