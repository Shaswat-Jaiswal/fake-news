import os
import pickle
import pandas as pd
from scipy.sparse import hstack
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

# Import preprocessing from project
from ..preprocessing.text_cleaner import clean_text

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "../models"))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "../data"))
TEST_CSV = os.path.join(DATA_DIR, "fakenewsnet_clean.csv")

LR_MODEL_PATH = os.path.join(MODEL_DIR, "lr", "model_lr.pkl")
LR_VEC_PATH   = os.path.join(MODEL_DIR, "lr", "vectorizer_lr.pkl")

NB_MODEL_PATH = os.path.join(MODEL_DIR, "nb", "model_nb.pkl")
NB_VEC_PATH   = os.path.join(MODEL_DIR, "nb", "vectorizer_nb.pkl")

SVM_MODEL_PATH = os.path.join(MODEL_DIR, "svm", "model_svm.pkl")
SVM_WORD_VEC_PATH = os.path.join(MODEL_DIR, "svm", "word_vectorizer.pkl")
SVM_CHAR_VEC_PATH = os.path.join(MODEL_DIR, "svm", "char_vectorizer.pkl")


def preprocess_text(text):
    return clean_text(text, lemmatize=True, remove_stopwords=True, spell_check=False)


def load_models():
    lr_model = pickle.load(open(LR_MODEL_PATH, "rb"))
    lr_vectorizer = pickle.load(open(LR_VEC_PATH, "rb"))

    nb_model = pickle.load(open(NB_MODEL_PATH, "rb"))
    nb_vectorizer = pickle.load(open(NB_VEC_PATH, "rb"))

    svm_model = pickle.load(open(SVM_MODEL_PATH, "rb"))
    svm_word_vectorizer = pickle.load(open(SVM_WORD_VEC_PATH, "rb"))
    svm_char_vectorizer = pickle.load(open(SVM_CHAR_VEC_PATH, "rb"))

    return (lr_model, lr_vectorizer, nb_model, nb_vectorizer,
            svm_model, svm_word_vectorizer, svm_char_vectorizer)


def ensemble_predict_text(cleaned, models):
    lr_model, lr_vectorizer, nb_model, nb_vectorizer, svm_model, svm_word_vectorizer, svm_char_vectorizer = models

    lr_p = lr_model.predict_proba(lr_vectorizer.transform([cleaned]))[0]
    nb_p = nb_model.predict_proba(nb_vectorizer.transform([cleaned]))[0]

    svm_vec = hstack([
        svm_word_vectorizer.transform([cleaned]),
        svm_char_vectorizer.transform([cleaned])
    ])
    svm_p = svm_model.predict_proba(svm_vec)[0]

    votes = [lr_p.argmax(), nb_p.argmax(), svm_p.argmax()]
    final = max(set(votes), key=votes.count)

    return final


def evaluate(test_csv=TEST_CSV):
    print(f"Loading test set from {test_csv}...")
    df = pd.read_csv(test_csv)

    if 'text' not in df.columns or 'label' not in df.columns:
        raise ValueError("Expected CSV with 'text' and 'label' columns")

    models = load_models()

    y_true = []
    y_pred = []

    for _, row in df.iterrows():
        text = str(row['text'])
        label = int(row['label'])

        cleaned = preprocess_text(text)
        pred = ensemble_predict_text(cleaned, models)

        y_true.append(label)
        y_pred.append(pred)

    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary', pos_label=1)

    print("Evaluation results for ensemble (majority vote of LR/NB/SVM):")
    print(f"Accuracy: {acc:.4f}")
    print(f"Precision (pos=1): {precision:.4f}")
    print(f"Recall (pos=1): {recall:.4f}")
    print(f"F1 (pos=1): {f1:.4f}\n")

    print("Full classification report:\n")
    print(classification_report(y_true, y_pred, digits=4))


if __name__ == "__main__":
    evaluate()
