import os
import pandas as pd
from difflib import SequenceMatcher

# ===============================
# DATASET PATHS
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "../.."))

FAKENEWSNET_PATH = os.path.join(DATA_DIR, "fakenewsnet_clean.csv")
NEWS_PATH = os.path.join(DATA_DIR, "news.csv")

# ===============================
# LOAD DATASETS (Cache them)
# ===============================
_dataset_cache = None

def load_datasets():
    """Load all datasets into memory once"""
    global _dataset_cache
    
    if _dataset_cache is not None:
        return _dataset_cache
    
    try:
        datasets = []
        
        # Load FakeNewsNet
        if os.path.exists(FAKENEWSNET_PATH):
            df_fake = pd.read_csv(FAKENEWSNET_PATH)
            if 'text' in df_fake.columns and 'label' in df_fake.columns:
                datasets.append(df_fake)
                print(f"✅ Loaded FakeNewsNet: {len(df_fake)} articles")
        
        # Load news.csv
        if os.path.exists(NEWS_PATH):
            df_news = pd.read_csv(NEWS_PATH)
            if 'text' in df_news.columns and 'label' in df_news.columns:
                datasets.append(df_news)
                print(f"✅ Loaded news.csv: {len(df_news)} articles")
        
        if datasets:
            _dataset_cache = pd.concat(datasets, ignore_index=True)
            print(f"✅ Total dataset size: {len(_dataset_cache)} articles")
            return _dataset_cache
        else:
            print("⚠️ No datasets found")
            return None
            
    except Exception as e:
        print(f"❌ Error loading datasets: {str(e)}")
        return None

# ===============================
# STRING SIMILARITY MATCHING
# ===============================
def string_similarity(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def find_dataset_match(text: str, similarity_threshold: float = 0.75) -> dict:
    """
    Search for exact or similar match in datasets
    Returns: {"found": bool, "label": 0/1, "similarity": float, "original_text": str}
    """
    try:
        dataset = load_datasets()
        
        if dataset is None or len(dataset) == 0:
            return {"found": False, "label": None, "similarity": 0.0, "source": "no_data"}
        
        # Exact match (fastest)
        exact_matches = dataset[dataset['text'].str.lower() == text.lower()]
        if len(exact_matches) > 0:
            label = exact_matches.iloc[0]['label']
            return {
                "found": True,
                "label": int(label),
                "similarity": 1.0,
                "source": "exact_match",
                "original_text": exact_matches.iloc[0]['text']
            }
        
        # Similarity matching (more lenient)
        input_len = len(text)
        best_match = None
        best_similarity = 0.0
        
        for idx, row in dataset.iterrows():
            dataset_text = str(row['text'])
            
            # Skip if length difference is too large (optimization)
            if abs(len(dataset_text) - input_len) > len(text) * 0.5:
                continue
            
            sim = string_similarity(text, dataset_text)
            
            if sim > best_similarity:
                best_similarity = sim
                best_match = row
        
        # Return match if similarity exceeds threshold
        if best_similarity >= similarity_threshold:
            return {
                "found": True,
                "label": int(best_match['label']),
                "similarity": round(best_similarity, 3),
                "source": "similarity_match",
                "original_text": best_match['text']
            }
        
        return {"found": False, "label": None, "similarity": best_similarity, "source": "no_match"}
        
    except Exception as e:
        print(f"❌ Dataset matching error: {str(e)}")
        return {"found": False, "label": None, "similarity": 0.0, "source": "error", "error": str(e)}

# ===============================
# INITIALIZE DATASETS ON MODULE LOAD
# ===============================
print("🔄 Initializing dataset matcher...")
load_datasets()
