# app1.py - Flask API for Phishing URL Detection & Analysis

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
import pickle
import traceback
import re
from urllib.parse import urlparse

from feature1 import FeatureExtraction
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# -------------------- App Setup --------------------
app = Flask(__name__)
CORS(app)

# -------------------- Load ML Model --------------------
try:
    with open("pickle/hybrid_stacking_model.pkl", "rb") as f:
        model = pickle.load(f)
    print("[INFO] Model loaded successfully.")
except Exception as e:
    model = None
    print("[ERROR] Model loading failed:", e)

# -------------------- Utility Functions --------------------
def is_valid_url(url):
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def get_registered_domain(url):
    host = urlparse(url).netloc.lower()

    # remove www
    if host.startswith("www."):
        host = host[4:]

    parts = host.split(".")

    # handle .gov.in, .nic.in, .ac.in, .edu.in
    if len(parts) >= 3 and parts[-2] in {"gov", "nic", "ac", "edu"} and parts[-1] == "in":
        return ".".join(parts[-3:])

    # normal domains (google.com, linkedin.com)
    if len(parts) >= 2:
        return ".".join(parts[-2:])

    return host

# -------------------- Trusted Domains --------------------
TRUSTED_DOMAINS = {
    "youtube.com",
    "google.com",
    "gmail.com",
    "facebook.com",
    "instagram.com",
    "amazon.com",
    "microsoft.com",
    "github.com"
    "linkedin.com"
}

TRUSTED_TLDS = {
    ".gov",
    ".gov.in",
    ".edu",
    ".edu.in",
    ".ac.in",
    ".nic.in",
    ".mil"
}

def is_trusted_tld(domain):
    return any(domain.endswith(tld) for tld in TRUSTED_TLDS)

# -------------------- Heuristic Detection --------------------
def heuristic_is_phishing(url: str) -> bool:
    """
    Only triggers on strong signals to avoid false positives.
    Legitimate URLs with keywords like 'login' or 'account' should
    still reach the ML model.
    """
    if not is_valid_url(url):
        return True

    domain = get_registered_domain(url)

    # Trusted domains bypass heuristics
    if domain in TRUSTED_DOMAINS or is_trusted_tld(domain):
        return False

    url_lower = url.lower()

    suspicious_keywords = [
        "secure", "login", "verify",
        "update", "account", "bank", "paypal"
    ]
    has_keyword = any(keyword in url_lower for keyword in suspicious_keywords)

    # Only flag if BOTH a suspicious keyword AND excessive subdomains are present
    # e.g. paypal.secure.login.xyz.com — strong phishing signal
    if has_keyword and len(domain.split(".")) > 3:
        return True

    return False

# -------------------- Health Check --------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Phishing URL Detection API is running!"})

# -------------------- Predict Endpoint --------------------
@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 503

    try:
        data = request.get_json(force=True, silent=True)
        url = data.get("url", "").strip()

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        print(f"[DEBUG] URL received: {url}")

        domain = get_registered_domain(url)

        # ✅ ABSOLUTE TRUSTED DOMAIN OVERRIDE
        if domain in TRUSTED_DOMAINS or is_trusted_tld(domain):
            return jsonify({
                "url": url,
                "prediction": "safe",
                "confidence": None,
                "note": "Trusted domain"
            })

        # -------- Heuristic Check --------
        if heuristic_is_phishing(url):
            return jsonify({
                "url": url,
                "prediction": "phishing",
                "confidence": None,
                "note": "Detected by heuristics"
            })

        # -------- Feature Extraction --------
        extractor = FeatureExtraction(url)
        features = np.array(
            extractor.getFeaturesList(),
            dtype=float
        ).reshape(1, -1)

        # Neutralize missing values (-1 → 0)
        features[features < 0] = 0

        expected_n = getattr(model, "n_features_in_", None)
        if expected_n and features.shape[1] != expected_n:
            return jsonify({
                "error": "Feature mismatch",
                "detail": f"Expected {expected_n}, got {features.shape[1]}"
            }), 500

        # -------- ML Prediction --------
        pred = model.predict(features)[0]
        label = "phishing" if pred == 1 else "safe"

        confidence = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(features)[0]
            confidence = round(
                probs[list(model.classes_).index(pred)] * 100, 2
            )

        # Suspicious state for low confidence phishing
        if label == "phishing" and confidence is not None and confidence < 70:
            label = "suspicious"

        return jsonify({
            "url": url,
            "prediction": label,
            "confidence": confidence,
            "note": "Predicted by ML model"
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": "Internal server error",
            "detail": str(e)
        }), 500

# -------------------- Analysis Endpoint --------------------
@app.route("/analysis", methods=["GET"])
def analysis():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 503

    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import confusion_matrix

        df = pd.read_csv("dataset_cybersecurity_michelle.csv")

        X = df.drop(columns=["phishing"])
        y = df["phishing"]

        # Match exact split used during training
        _, X_test, _, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        y_pred = model.predict(X_test.values)

        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()

        metrics = {
            "accuracy":  round(accuracy_score(y_test, y_pred) * 100, 2),
            "precision": round(precision_score(y_test, y_pred) * 100, 2),
            "recall":    round(recall_score(y_test, y_pred) * 100, 2),
            "f1_score":  round(f1_score(y_test, y_pred) * 100, 2),
        }

        return jsonify({
            "model_info": {
                "name": "Hybrid Stacking Model",
                "base_learners": ["Random Forest", "Decision Tree"],
                "type": "Stacking Ensemble"
            },
            "metrics": metrics,
            "samples_evaluated": int(len(y_test)),
            "confusion": {
                "true_negative":  int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive":  int(tp),
            }
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": "Analysis failed",
            "detail": str(e)
        }), 500

# -------------------- Contact Endpoint --------------------
@app.route("/contact", methods=["POST"])
def contact():
    try:
        data = request.get_json(force=True, silent=True)

        name    = data.get("name", "").strip()
        email   = data.get("email", "").strip()
        message = data.get("message", "").strip()

        if not name or not email or not message:
            return jsonify({"error": "All fields are required"}), 400

        if not is_valid_email(email):
            return jsonify({"error": "Invalid email address"}), 400

        with open("contact_messages.txt", "a", encoding="utf-8") as f:
            f.write(
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Message: {message}\n"
                f"{'-' * 40}\n"
            )

        return jsonify({"success": "Message sent successfully"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Failed to send message"}), 500

# -------------------- Run App --------------------
if __name__ == "__main__":
    app.run(debug=True)