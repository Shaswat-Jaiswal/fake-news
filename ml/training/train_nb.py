import pandas as pd
import pickle
import re
import os
import sys

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report

# ===============================
# PATHS
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../.."))

# Add project root to sys.path
sys.path.append(PROJECT_ROOT)

from ..preprocessing.text_cleaner import clean_text

DATA_DIR = os.path.join(PROJECT_ROOT, "ml", "data")
MODEL_DIR = os.path.join(PROJECT_ROOT, "ml", "models", "nb")

os.makedirs(MODEL_DIR, exist_ok=True)


df1 = pd.read_csv(os.path.join(DATA_DIR, "news.csv"))[["text", "label"]]
df2 = pd.read_csv(os.path.join(DATA_DIR, "fakenewsnet_clean.csv"))[["text", "label"]]
df3 = pd.read_csv(os.path.join(DATA_DIR, "Book1.csv"), encoding="latin1")[["text", "label"]]

df = pd.concat([df1, df2, df3], ignore_index=True)
df.dropna(inplace=True)

print("📦 Total rows:", len(df))

df["text"] = df["text"].apply(clean_text)

X = df["text"]
y = df["label"]

# ===============================
# TF-IDF
# ===============================
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    min_df=3,
    max_df=0.9,
    max_features=50000
)

X_vec = vectorizer.fit_transform(X)

# ===============================
# SPLIT
# ===============================
X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=7, stratify=y
)

# ===============================
# NAIVE BAYES
# ===============================
model = MultinomialNB(alpha=0.5)
model.fit(X_train, y_train)

# ===============================
# EVALUATION
# ===============================
y_pred = model.predict(X_test)
print("\n🔥 Accuracy:",
      round(accuracy_score(y_test, y_pred) * 100, 2), "%\n")
print(classification_report(y_test, y_pred))

# ===============================
# SAVE
# ===============================
pickle.dump(model, open(os.path.join(MODEL_DIR, "model_nb.pkl"), "wb"))
pickle.dump(vectorizer, open(os.path.join(MODEL_DIR, "vectorizer_nb.pkl"), "wb"))

print("\n✅ Model & vectorizer saved")
