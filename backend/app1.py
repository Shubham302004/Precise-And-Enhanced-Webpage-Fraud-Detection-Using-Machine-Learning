# app1.py - Flask API for Phishing URL Detection & Analysis

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
import pickle
import traceback
import re
import os
from urllib.parse import urlparse
from uuid import uuid4

from feature1 import FeatureExtraction, FEATURE_ORDER
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# -------------------- App Setup --------------------
app = Flask(__name__)
CORS(app)

# Never expose the Werkzeug debugger outside local development: the debug
# console is effectively remote code execution if this port is reachable.
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

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
    "github.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "apple.com",
    "cloudflare.com",
    "wikipedia.org",
    "stackoverflow.com"
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

    # Full hostname (keeps subdomains): paypal.secure.login.xyz.com -> 6 labels.
    # NOTE: get_registered_domain() collapses to 2-3 labels, so measuring
    # subdomain depth must be done on the raw host, not the registered domain.
    host = urlparse(url).netloc.lower().split(":")[0]
    host_labels = [p for p in host.split(".") if p]

    suspicious_keywords = [
        "secure", "login", "verify",
        "update", "account", "bank", "paypal"
    ]
    has_keyword = any(keyword in url_lower for keyword in suspicious_keywords)

    # Only flag if BOTH a suspicious keyword AND excessive subdomains are present
    # e.g. paypal.secure.login.xyz.com — strong phishing signal
    # (a plain "login.example.com" stays on 3 labels and still reaches the model)
    if has_keyword and len(host_labels) > 4:
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
        data = request.get_json(force=True, silent=True) or {}
        url = str(data.get("url", "")).strip()

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        # Bound input size: real URLs are short, and feature extraction
        # performs network lookups on whatever we are given.
        if len(url) > 2048:
            return jsonify({"error": "URL too long (max 2048 characters)"}), 400

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
                "expected": int(expected_n),
                "got": int(features.shape[1]),
                "request_id": uuid4().hex[:12]
            }), 500

        # The model was fitted on a DataFrame, so hand it a DataFrame with the
        # same column names - a bare ndarray makes sklearn warn and skips any
        # column-name validation the estimators were trained with.
        features_df = pd.DataFrame(features, columns=FEATURE_ORDER)

        # -------- ML Prediction --------
        pred = model.predict(features_df)[0]
        label = "phishing" if pred == 1 else "safe"

        confidence = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(features_df)[0]
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
        # Log the real error server-side; return a generic message so internal
        # details (paths, library versions, tracebacks) never reach the client.
        return jsonify({
            "error": "Internal server error",
            "request_id": uuid4().hex[:12]  # match against the traceback in the logs
        }), 500

# -------------------- Analysis Endpoint --------------------
# Metrics depend only on (dataset, model), both of which are immutable at
# runtime, so the expensive part (34 MB CSV read + ~26k predictions) is
# computed once and cached instead of on every GET.
_ANALYSIS_CACHE = {}

def _build_analysis_payload():
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import confusion_matrix

    df = pd.read_csv("dataset_cybersecurity_michelle.csv")

    X = df.drop(columns=["phishing"])
    y = df["phishing"]

    # Match exact split used during training
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # X_test is already a DataFrame with the training column names.
    y_pred = model.predict(X_test)

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        "accuracy":  round(accuracy_score(y_test, y_pred) * 100, 2),
        "precision": round(precision_score(y_test, y_pred) * 100, 2),
        "recall":    round(recall_score(y_test, y_pred) * 100, 2),
        "f1_score":  round(f1_score(y_test, y_pred) * 100, 2),
    }

    return {
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
    }

@app.route("/analysis", methods=["GET"])
def analysis():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 503

    try:
        if not _ANALYSIS_CACHE:
            _ANALYSIS_CACHE.update(_build_analysis_payload())
        return jsonify(_ANALYSIS_CACHE)

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": "Analysis failed",
            "request_id": uuid4().hex[:12]
        }), 500

# -------------------- Contact Endpoint --------------------
@app.route("/contact", methods=["POST"])
def contact():
    try:
        data = request.get_json(force=True, silent=True) or {}

        # Newlines in name/message would forge extra entries in the log file,
        # so they are replaced with spaces before any length checks.
        name    = str(data.get("name", "")).strip().replace("\r", " ").replace("\n", " ")
        email   = str(data.get("email", "")).strip().replace("\r", " ").replace("\n", " ")
        message = str(data.get("message", "")).strip().replace("\r", " ")

        if not name or not email or not message:
            return jsonify({"error": "All fields are required"}), 400

        if len(name) > 100 or len(email) > 254 or len(message) > 2000:
            return jsonify({"error": "Field too long"}), 400

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
    # debug defaults to off; enable locally with FLASK_DEBUG=1 python app1.py
    app.run(debug=DEBUG)