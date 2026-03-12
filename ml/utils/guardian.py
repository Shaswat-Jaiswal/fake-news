import os
import requests

GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")

def guardian_strong_match(text: str) -> bool:
    """
    Check if news text matches Guardian's verified articles
    Returns True if strong match found
    """
    if not GUARDIAN_API_KEY:
        return False

    try:
        # Extract first 10 words as keywords for Guardian search
        keywords = " ".join(text.lower().split()[:10])
        
        url = "https://content.guardianapis.com/search"
        params = {
            "q": keywords,
            "api-key": GUARDIAN_API_KEY,
            "page-size": 10  # Increased from 5 for better matching
        }

        res = requests.get(url, params=params, timeout=10).json()
        results = res.get("response", {}).get("results", [])

        if not results:
            return False

        # Extract important words (exclude common words)
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", 
                     "and", "or", "but", "in", "on", "at", "to", "for", "of", 
                     "by", "with", "as", "has", "have", "had", "do", "does", "did",
                     "that", "this", "it", "from", "up", "about"}
        
        text_words = set(word.lower() for word in text.split() if len(word) > 2 and word.lower() not in stop_words)

        # Check each Guardian article
        for article in results:
            title = article.get("webTitle", "")
            
            # Word overlap matching
            title_words = set(word.lower() for word in title.split() if len(word) > 2 and word.lower() not in stop_words)
            
            if not title_words:
                continue
                
            overlap = len(text_words & title_words)
            ratio = overlap / max(len(text_words), 1)

            # 🔥 Strong match criteria:
            # - At least 50% word overlap (improved from 60%)
            # - At least 3 common words
            if ratio >= 0.5 and overlap >= 3:
                return True
            
            # OR: Very high overlap (60%+) with at least 2 matching words
            if ratio >= 0.6 and overlap >= 2:
                return True

        return False
    
    except Exception as e:
        print(f"⚠️ Guardian API Error: {str(e)}")
        # If Guardian API fails, don't mark as verified
        return False 