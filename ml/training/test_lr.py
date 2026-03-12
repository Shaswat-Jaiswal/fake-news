import pandas as pd
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

from ..preprocessing.text_cleaner import clean_text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../.."))

DATA_DIR = os.path.join(PROJECT_ROOT, "ml", "data")
MODEL_DIR = os.path.join(PROJECT_ROOT, "ml", "models", "lr")

os.makedirs(MODEL_DIR, exist_ok=True)

# ===============================
# LOAD DATA
# ===============================
df1 = pd.read_csv(os.path.join(DATA_DIR, "news.csv"))
df2 = pd.read_csv(os.path.join(DATA_DIR, "fakenewsnet_clean.csv"))
df3 = pd.read_csv(os.path.join(DATA_DIR, "Book1.csv"), encoding="latin1")

df = pd.concat([df1, df2, df3], ignore_index=True)
df.dropna(inplace=True)

print("📦 Total rows:", len(df))

# ===============================
# CLEAN TEXT
# ===============================
df["text"] = df["text"].apply(clean_text)

X = df["text"]
y = df["label"]

# ===============================
# TF-IDF
# ===============================
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    max_features=50000,
    min_df=5,
    max_df=0.85,
    sublinear_tf=True
)

X_vec = vectorizer.fit_transform(X)

# ===============================
# SPLIT
# ===============================
X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42, stratify=y
)

# ===============================
# MODEL
# ===============================
model = LogisticRegression(
    max_iter=3000,
    C=4,
    solver="saga",
    class_weight={0: 2.5, 1: 1},
    n_jobs=-1
)

model.fit(X_train, y_train)

# ===============================
# EVALUATION
# ===============================
y_pred = model.predict(X_test)
print("🔥 Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# ===============================
# SAVE
# ===============================
pickle.dump(model, open(os.path.join(MODEL_DIR, "model_lr.pkl"), "wb"))
pickle.dump(vectorizer, open(os.path.join(MODEL_DIR, "vectorizer_lr.pkl"), "wb"))

print("✅ LR model saved successfully")
