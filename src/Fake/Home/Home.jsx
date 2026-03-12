import { useState } from "react";
import { MdArticle } from "react-icons/md";
import { LuLoader } from "react-icons/lu";
import { Navbar } from  "../Nav/Navbar.jsx";
import { Hams } from "../Hams/Hams.jsx";
import { analyzeNews } from "../api/newsApi.js";
import "./Home.css";

export const Home = () => {
    const[input, setInput] = useState("");
    const[loading, setLoading] = useState(false);
    const[result, setResult] = useState("");

    const handleAnalyze = async  () => {
        if(!input.trim()){
            alert("please enter news text");
            return;
        }
       setLoading(true);
       
       try {
           const response = await analyzeNews(input);
           setResult(response.data);
       } catch (error) {
           console.error("Analysis error:", error);
           setResult({ 
               error: error.response?.data?.message || "Analysis failed. Please try again." 
           });
       } finally {
           setLoading(false);
       }
    }


     
  const wordCount = input.trim() === "" ? 0 : input.trim().split(/\s+/).length;
  const readTime = Math.ceil(wordCount / 200);

    return(
        <div className="container-1">
            <div className="top-bar">
              <Hams />
                 <Navbar />
            </div>
            <div className="main-container">
          <div className="heading-box">
            <MdArticle size={35} className="heading-icon" />
            <h2>Analyse News </h2>
          </div>
          
          <div className="big-inputbox">
            <textarea
            placeholder="Enter headline or your news text..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="fixed-textarea"
            ></textarea>
             
             <div className="clear-row">
                <button
                className="clear-btn"
                onClick={() => {
                    setInput("");
                    setResult("");
                 }}
                >
                    Clear
                </button>
             </div>
          </div>

         <p className="char-count">
           Characters: {input.length} • Words: {wordCount} • Read time: {readTime} min
            </p> 
           
           <button className="analyze-button" onClick={handleAnalyze} disabled={loading}>
             {loading ? (
                <span className="loader-box">
                    <LuLoader className="spin" size={22} /> Analyzing...
                </span>
             ): (
            "Analyze News"
             )}
           </button>
           
           {result && (
          <div className="result-box">
            <h3>Result:</h3>
            {result.error ? (
              <p className="error">{result.error}</p>
            ) : (
              <div>
                <p><strong>Prediction:</strong> {result.prediction}</p>
                <p><strong>Confidence:</strong> {result.confidence}%</p>
                {result.reason && <p><strong>Reason:</strong> {result.reason}</p>}
                {result.source && <p><strong>Source:</strong> {result.source}</p>}
              </div>
            )}
          </div>
        )}
            </div>
        </div>
    );
};