import pandas as pd
import pickle
import os
from scipy.sparse import hstack

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, classification_report, precision_recall_fscore_support
import json

from ..preprocessing.text_cleaner import clean_text

# ===============================
# PATHS
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../.."))

DATA_DIR = os.path.join(PROJECT_ROOT, "ml", "data")
MODEL_DIR = os.path.join(PROJECT_ROOT, "ml", "models", "svm")

os.makedirs(MODEL_DIR, exist_ok=True)

# ===============================
# LOAD DATA
# ===============================
df1 = pd.read_csv(os.path.join(DATA_DIR, "news.csv"))[["text", "label"]]
df2 = pd.read_csv(os.path.join(DATA_DIR, "fakenewsnet_clean.csv"))[["text", "label"]]
df3 = pd.read_csv(os.path.join(DATA_DIR, "Book1.csv"), encoding="latin1")[["text", "label"]]

df = pd.concat([df1, df2, df3], ignore_index=True)
df.dropna(inplace=True)

# ===============================
# PREPROCESSING
# ===============================
df["text"] = df["text"].apply(clean_text)

X = df["text"]
y = df["label"]

# ===============================
# TF-IDF
# ===============================
word_vectorizer = TfidfVectorizer(
    ngram_range=(1, 3),
    min_df=2,
    max_df=0.85,
    sublinear_tf=True,
    max_features=80000
)

char_vectorizer = TfidfVectorizer(
    analyzer="char_wb",
    ngram_range=(3, 5),
    min_df=5,
    sublinear_tf=True,
    max_features=15000
)

X_word = word_vectorizer.fit_transform(X)
X_char = char_vectorizer.fit_transform(X)

X_final = hstack([X_word, X_char])

# ===============================
# SPLIT
# ===============================
X_train, X_test, y_train, y_test = train_test_split(
    X_final,
    y,
    test_size=0.2,
    random_state=7,
    stratify=y
)

# ===============================
# MODEL
# ===============================
svm = LinearSVC(
    C=6,
    class_weight={0: 1.4, 1: 1.0},
    max_iter=15000
)

model = CalibratedClassifierCV(
    svm,
    method="sigmoid",
    cv=5
)

model.fit(X_train, y_train)

# ===============================
# EVALUATION
# ===============================
y_pred = model.predict(X_test)

print("\n🔥 Accuracy:", round(accuracy_score(y_test, y_pred) * 100, 2), "%\n")
print(classification_report(y_test, y_pred))

# explicit precision/recall/f1 (per-class and averages)
labels = sorted(list(set(y_test)))
prec_per, rec_per, f1_per, sup_per = precision_recall_fscore_support(y_test, y_pred, labels=labels, zero_division=0)
prec_micro, rec_micro, f1_micro, _ = precision_recall_fscore_support(y_test, y_pred, average="micro", zero_division=0)
prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(y_test, y_pred, average="macro", zero_division=0)

print("Precision (macro):", round(prec_macro, 4))
print("Recall (macro):", round(rec_macro, 4))
print("F1-score (macro):", round(f1_macro, 4))
print("Precision (micro):", round(prec_micro, 4))
print("Recall (micro):", round(rec_micro, 4))
print("F1-score (micro):", round(f1_micro, 4))

# save metrics to file
metrics = {
    "accuracy": round(accuracy_score(y_test, y_pred), 6),
    "macro": {"precision": round(prec_macro, 6), "recall": round(rec_macro, 6), "f1": round(f1_macro, 6)},
    "micro": {"precision": round(prec_micro, 6), "recall": round(rec_micro, 6), "f1": round(f1_micro, 6)},
    "per_class": {}
}

for lbl, p, r, f, s in zip(labels, prec_per, rec_per, f1_per, sup_per):
    metrics["per_class"][str(lbl)] = {"precision": round(p, 6), "recall": round(r, 6), "f1": round(f, 6), "support": int(s)}

with open(os.path.join(MODEL_DIR, "metrics_svm.json"), "w", encoding="utf-8") as fh:
    json.dump(metrics, fh, indent=2)

print(f"\n✅ Metrics saved to: {os.path.join(MODEL_DIR, 'metrics_svm.json')}")

# ===============================
# SAVE
# ===============================
pickle.dump(model, open(os.path.join(MODEL_DIR, "model_svm.pkl"), "wb"))
pickle.dump(word_vectorizer, open(os.path.join(MODEL_DIR, "word_vectorizer.pkl"), "wb"))
pickle.dump(char_vectorizer, open(os.path.join(MODEL_DIR, "char_vectorizer.pkl"), "wb"))

print("\n✅ Stable SVM model saved")
