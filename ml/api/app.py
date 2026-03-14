from flask import Flask, request, jsonify
import pickle
import os
from scipy.sparse import hstack

# ===============================
# INTERNAL IMPORTS
# ===============================
from ..utils.guardian import guardian_strong_match
from ..utils.non_news import is_non_news
from ..utils.dataset_matcher import find_dataset_match
from ..preprocessing.text_cleaner import clean_text
from ..utils.rules import rule_based_check, validate_person_names

# ===============================
# FLASK APP
# ===============================
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ===============================
# MODEL PATHS
# ===============================
MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "../models"))

LR_MODEL_PATH = os.path.join(MODEL_DIR, "lr", "model_lr.pkl")
LR_VEC_PATH   = os.path.join(MODEL_DIR, "lr", "vectorizer_lr.pkl")

NB_MODEL_PATH = os.path.join(MODEL_DIR, "nb", "model_nb.pkl")
NB_VEC_PATH   = os.path.join(MODEL_DIR, "nb", "vectorizer_nb.pkl")

SVM_MODEL_PATH = os.path.join(MODEL_DIR, "svm", "model_svm.pkl")
SVM_WORD_VEC_PATH = os.path.join(MODEL_DIR, "svm", "word_vectorizer.pkl")
SVM_CHAR_VEC_PATH = os.path.join(MODEL_DIR, "svm", "char_vectorizer.pkl")

# ===============================
# LOAD MODELS
# ===============================
lr_model = pickle.load(open(LR_MODEL_PATH, "rb"))
lr_vectorizer = pickle.load(open(LR_VEC_PATH, "rb"))

nb_model = pickle.load(open(NB_MODEL_PATH, "rb"))
nb_vectorizer = pickle.load(open(NB_VEC_PATH, "rb"))

svm_model = pickle.load(open(SVM_MODEL_PATH, "rb"))
svm_word_vectorizer = pickle.load(open(SVM_WORD_VEC_PATH, "rb"))
svm_char_vectorizer = pickle.load(open(SVM_CHAR_VEC_PATH, "rb"))

# ===============================
# FAKE KEYWORDS
# ===============================
FAKE_KEYWORDS = {
    "alien", "ufo", "zombie", "time travel",
    "parallel universe", "dragon", "ghost"
}

# ===============================
# PREPROCESS
# ===============================
def preprocess_text(text):
    return clean_text(
        text,
        lemmatize=True,
        remove_stopwords=True,
        spell_check=False
    )

# ===============================
# ML ENSEMBLE
# ===============================
def ensemble_predict(text):
    try:
        cleaned = preprocess_text(text)

        # Check for obvious fake keywords
        for kw in FAKE_KEYWORDS:
            if kw in cleaned:
                return {"prediction": "Fake", "confidence": 99.0, "reason": "Fake keyword detected"}

        # Get predictions from all 3 models
        lr_p = lr_model.predict_proba(lr_vectorizer.transform([cleaned]))[0]
        nb_p = nb_model.predict_proba(nb_vectorizer.transform([cleaned]))[0]

        # SVM with combined word + char vectorizers
        svm_vec = hstack([
            svm_word_vectorizer.transform([cleaned]),
            svm_char_vectorizer.transform([cleaned])
        ])
        svm_p = svm_model.predict_proba(svm_vec)[0]

        # Ensemble voting: take majority vote
        votes = [lr_p.argmax(), nb_p.argmax(), svm_p.argmax()]
        final = max(set(votes), key=votes.count)

        # Calculate average confidence across all 3 models
        confidence = round((lr_p[final] + nb_p[final] + svm_p[final]) / 3 * 100, 2)

        return {
            "prediction": "Real" if final == 1 else "Fake",
            "confidence": confidence,
            "reason": "ML ensemble prediction"
        }
    
    except Exception as e:
        # Fallback to conservative prediction if ML fails
        print(f"❌ ML Analysis Error: {str(e)}")
        return {
            "prediction": "Fake",
            "confidence": 0.0,
            "reason": f"ML analysis error: {str(e)}"
        }

# ===============================
# ROUTES
# ===============================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API running ✅"})

# ===============================
# PREDICT ROUTE (Simple ML ensemble)
# ===============================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        text = request.json.get("text", "").strip()
        
        if not text:
            return jsonify({"error": "Text is empty"}), 400
        
        # =========================================
        try:
            dataset_result = find_dataset_match(text)
            
            if dataset_result["found"]:
                prediction = "Real" if dataset_result["label"] == 1 else "Fake"
                return jsonify({
                    "prediction": prediction,
                    "confidence": round(dataset_result["similarity"] * 100, 2),
                    "source": "dataset",
                    "similarity": dataset_result["similarity"]
                })
        except Exception as e:
            print(f"⚠️ Dataset match error: {str(e)}")
        
        # 1️⃣ Check for fake people (unknown fictional names)
        valid = validate_person_names(text)
        if not valid["valid"]:
            return jsonify({
                "prediction": "Fake",
                "confidence": 99,
                "reason": valid["reason"]
            })
        
        # 2️⃣ Use ML ensemble prediction
        result = ensemble_predict(text)
        
        return jsonify({
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "reason": result["reason"]
        })
    
    except Exception as e:
        print(f"❌ Predict route error: {str(e)}")
        return jsonify({
            "prediction": "Fake",
            "confidence": 0.0,
            "error": str(e)
        }), 500

# ===============================
# FINAL CHECK ROUTE
# ===============================
@app.route("/check", methods=["POST"])
def check_news():
    text = request.json.get("text", "").strip()

    if not text:
        return jsonify({"error": "Text is empty"}), 400

    source_verification = []

    # 4️⃣ Guardian verification (check against real news sources)
    guardian_real = guardian_strong_match(text)
    if guardian_real:
        source_verification.append("Published in The Guardian.")

    # Check dataset match
    dataset_result = None
    try:
        dataset_result = find_dataset_match(text)
        if dataset_result["found"]:
            source_verification.append("Cross-referenced with database.")
    except Exception as e:
        print(f"⚠️ Dataset match error: {str(e)}")

    # If dataset found, return with dataset prediction
    if dataset_result and dataset_result["found"]:
        prediction = "Real" if dataset_result["label"] == 1 else "Fake"
        return jsonify({
            "prediction": prediction,
            "confidence": round(dataset_result["similarity"] * 100, 2),
            "source": "dataset",
            "similarity": dataset_result["similarity"],
            "source_verification": source_verification
        })

    # 1️⃣ Non-news (casual statements like weather, college closure, etc.)
    if is_non_news(text):
        return jsonify({"prediction": "Fake", "confidence": 90, "reason": "Casual/non-news statement"})

    # 2️⃣ Fake people (unknown fictional names)
    valid = validate_person_names(text)
    if not valid["valid"]:
        return jsonify({"prediction": "Fake", "confidence": 100, "reason": valid["reason"]})

    # 3️⃣ Rule-based (death claims about real people)
    if not rule_based_check(text):
        return jsonify({"prediction": "Fake", "confidence": 100, "reason": "Death claim rule violation"})

    # 4️⃣ Guardian verification (check against real news sources)
    guardian_real = guardian_strong_match(text)
    if guardian_real:
        source_verification.append("Published in The Guardian.")

    # Decide prediction
    if guardian_real:
        response = {
            "prediction": "Real",
            "confidence": 95,
            "source": "guardian",
            "source_verification": source_verification
        }
    else:
        response = {
            "prediction": "Real",
            "confidence": 80,
            "source": "default"
        }

    return jsonify(response)
# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)