"""
text_cleaner.py
Advanced Text Cleaning for Fake News Detection

Supports:
- Logistic Regression
- Naive Bayes
- SVM
- TF-IDF pipelines

Features:
✔ URL removal
✔ Stopword removal
✔ Lemmatization
✔ Repeated letter normalization
✔ Optional spell correction (SymSpell)
✔ Safe NLTK download
✔ DataFrame support
"""

import re
import unicodedata
import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# =====================================
# NLTK SAFE DOWNLOAD
# =====================================
def _ensure_nltk():
    try:
        stopwords.words("english")
    except LookupError:
        nltk.download("stopwords")
        nltk.download("wordnet")
        nltk.download("omw-1.4")


_ensure_nltk()


# =====================================
# GLOBAL OBJECTS
# =====================================
STOP_WORDS = set(stopwords.words("english"))

# Important words kept for fake news meaning
STOP_WORDS -= {"no", "not", "never", "against"}

LEMMATIZER = WordNetLemmatizer()


# =====================================
# SPELL CHECK CONFIG
# =====================================
SPELL_CHECK_ENABLED = False
SYM_SPELL = None

if SPELL_CHECK_ENABLED:
    try:
        from symspellpy import SymSpell, Verbosity
        import pkg_resources

        SYM_SPELL = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

        dictionary_path = pkg_resources.resource_filename(
            "symspellpy",
            "frequency_dictionary_en_82_765.txt"
        )

        SYM_SPELL.load_dictionary(dictionary_path, 0, 1)

    except Exception:
        SPELL_CHECK_ENABLED = False
        SYM_SPELL = None


# =====================================
# NORMALIZE REPEATED CHARACTERS
# =====================================
def _normalize_spelling(word: str) -> str:
    """
    Reduce repeated characters
    Example:
    gooooood -> good
    """
    return re.sub(r"(.)\1{2,}", r"\1\1", word)


# =====================================
# HEAVY SPELL CORRECTION
# =====================================
def _spell_correct(word: str) -> str:
    if not SPELL_CHECK_ENABLED or SYM_SPELL is None:
        return word

    suggestions = SYM_SPELL.lookup(
        word,
        Verbosity.CLOSEST,
        max_edit_distance=2
    )

    return suggestions[0].term if suggestions else word


# =====================================
# MAIN TEXT CLEANING FUNCTION
# =====================================
def clean_text(
    text: str,
    *,
    remove_stopwords: bool = True,
    lemmatize: bool = True,
    spell_check: bool = False
) -> str:
    """
    Clean raw text for ML models
    """

    if not isinstance(text, str):
        return ""

    # Unicode normalize
    text = unicodedata.normalize("NFKD", text)

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Remove special characters
    text = re.sub(r"[^a-z0-9 ]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    tokens = []

    for word in text.split():

        # Remove stopwords
        if remove_stopwords and word in STOP_WORDS:
            continue

        # Remove short words
        if len(word) < 3:
            continue

        # Normalize repeated letters
        word = _normalize_spelling(word)

        # Optional spell correction
        if spell_check:
            word = _spell_correct(word)

        # Lemmatization
        if lemmatize:
            word = LEMMATIZER.lemmatize(word, pos="v")
            word = LEMMATIZER.lemmatize(word, pos="n")

        tokens.append(word)

    return " ".join(tokens)


# =====================================
# CLEAN DATAFRAME COLUMN
# =====================================
def clean_dataframe(df, column="text"):
    """
    Apply cleaning to pandas dataframe column
    """
    df[column] = df[column].apply(clean_text)
    return df


# =====================================
# TEST RUN
# =====================================
if __name__ == "__main__":

    sample = """
    Breaking!!! Trump said COVID is a hoooaax!!!
    Visit https://news.com for more details!!!
    """

    cleaned = clean_text(sample)

    print("Original:")
    print(sample)

    print("\nCleaned:")
    print(cleaned)
    