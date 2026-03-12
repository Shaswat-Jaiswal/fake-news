# src/utils/rules.py
import re

# ===============================
# VALID REAL PEOPLE (भारतीय राजनेता + अन्य)
# ===============================
VALID_PEOPLE = {
    # Prime Ministers
    "narendra modi", "pm modi", "rajiv gandhi", "indira gandhi", 
    "manmohan singh", "atal bihari vajpayee", "inder kumar gujral",
    "deve gowda", "l k advani", "p v narasimha rao",
    
    # Current Ministers
    "amit shah", "rajnath singh", "nirmala sitharaman", "nitin gadkari",
    "smriti irani", "piyush goyal", "bharati pawar", "ashwini vaishnaw",
    
    # Opposition Leaders
    "rahul gandhi", "priyanka gandhi", "mamata banerjee", "mk stalin",
    "arvind kejriwal", "nitesh kulkarni", "yechury", "sitaram yechury",
    "didi", "tejashwi yadav", "akhilesh yadav", "sharad pawar",
    
    # Other Known Figures
    "virat kohli", "salman khan", "shah rukh khan", "aamir khan",
    "amitabh bachchan", "ratan tata", "dhirubhai ambani", "mukesh ambani",
    "anil ambani", "gautam adani", "sundar pichai"
}

IMPORTANT_PEOPLE = list(VALID_PEOPLE)

DEATH_KEYWORDS = ["is dead", "has died", "killed", "passed away"]

# ===============================
# FUNCTION: Check if person name is VALID (not fictional)
# ===============================
def validate_person_names(text: str) -> dict:
    """
    Checks if text mentions UNKNOWN/FICTIONAL people
    Returns: {"valid": True/False, "invalid_names": [list], "reason": ""}
    """
    text_lower = text.lower()

    BLOCKED_ENTITIES = {
        "uit", "university", "college", "school",
        "weather", "temperature", "policy scheme",
        "today weather","weather is",
    "temperature today"
    }

    for entity in BLOCKED_ENTITIES:
        if entity in text_lower:
            return {
                "valid": False,
                "invalid_names": [entity],
                "reason": "Non-news or non-human entity detected"
            }
    mentioned_people = []

    # Allowed PM names (only these will be treated as valid when title is PM)
    ALLOWED_PM_NAMES = {"modi", "narendra modi"}
    # Match: pm <name> or pm <firstname lastname> (single or double names)
    pm_pattern = r'\b(pm|prime minister)\b\s+([a-z]+(?:\s[a-z]+)?)\b'
    matches = re.findall(pm_pattern, text_lower)

    invalid = []

    for title, name in matches:
        clean_name = name.strip().lower()
        # Check if name is in allowed list (exact match or partial match)
        is_valid = clean_name in ALLOWED_PM_NAMES
        
        if not is_valid:
            invalid.append(f"{title} {name}")

    if invalid:
        return {
            "valid": False,
            "invalid_names": invalid,
            "reason": "Unknown or fictional PM detected"
        }

    # --------------------------------------
    # 3️⃣ Otherwise valid
    # --------------------------------------

    return {
        "valid": True,
        "invalid_names": [],
        "reason": ""
    }

    # # Extract potential person names with optional title
    # pattern = r'(?:\b(pm|prime minister|minister)\b\s*)?([a-z][a-z\.\s]+?)\s+(?:launches|announces|says|declares|reveals|opens|introduces|unveils)'

    # matches = re.findall(pattern, text_lower)
    # # matches: list of tuples (title_or_empty, name)

    # invalid_names = []

    # for title, name in matches:
    #     clean_name = name.strip()

    #     # If title indicates PM, only allow ALLOWED_PM_NAMES
    #     if title and title.strip() in {"pm", "prime minister", "minister"}:
    #         is_allowed_pm = any(allowed in clean_name or clean_name in allowed for allowed in ALLOWED_PM_NAMES)
    #         if not is_allowed_pm:
    #             invalid_names.append(f"{title.strip()} {clean_name}")
    #         continue

    #     # For non-PM mentions, fall back to VALID_PEOPLE check
    #     is_valid = any(valid_name in clean_name or clean_name in valid_name for valid_name in VALID_PEOPLE)
    #     if not is_valid and len(clean_name) > 2:
    #         invalid_names.append(clean_name)

    # if invalid_names:
    #     return {
    #         "valid": False,
    #         "invalid_names": invalid_names,
    #         "reason": f"Mentioned unknown/fictional person detected: {', '.join(set(invalid_names))}"
    #     }

    # return {"valid": True, "invalid_names": [], "reason": ""}

# ===============================
# FUNCTION: Original rule check (death claims)
# ===============================
def rule_based_check(text: str) -> bool:
    text = text.lower()

    for person in IMPORTANT_PEOPLE:
        if person in text:
            for death_word in DEATH_KEYWORDS:
                if death_word in text:
                    return False   # ❌ FAIL RULE

    return True
