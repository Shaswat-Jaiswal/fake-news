import re

def is_non_news(text: str) -> bool:
    """
    Detects casual/non-news statements
    Returns True if text is NOT a news item
    """
    text = text.lower().strip()

    # Too short to be news
    if len(text.split()) < 5:
        return True

    # Casual conversation patterns
    casual_patterns = [
        r"today\s+weather",
        r"weather\s+is",
        r"college\s+is\s+closed",
        r"school\s+is\s+closed",
        r"i\s+am\s+feeling",
        r"very\s+bad\s+today",
        r"how\s+are\s+you",
        r"temperature\s+today",
        r"rain\s+today",
        r"my\s+mood",
        r"feeling\s+(good|bad)",
        r"(good|bad)\s+day\s+today",
        r"what\s+is.{0,20}weather",
        r"i\s+think\s+the\s+weather",
    ]

    for pattern in casual_patterns:
        if re.search(pattern, text):
            return True

    # Patterns with only personal opinions/feelings
    opinion_patterns = [
        r"^(i\s+think|in\s+my\s+opinion|i\s+believe|personally)",
    ]
    
    for pattern in opinion_patterns:
        if re.search(pattern, text):
            # If it's just personal opinion without news context
            if not any(keyword in text for keyword in ["said", "announced", "reported", "according", "sources", "official"]):
                return True

    return False 
