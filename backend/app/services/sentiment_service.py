
from pathlib import Path

import joblib


# Locate the trained ML model
BASE_DIR = Path(__file__).resolve().parents[3]

MODEL_PATH = BASE_DIR / "ml" / "sentiment_pipeline.joblib"


def load_sentiment_model():
    """Load the trained sentiment model."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Sentiment model not found at: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def predict_feedback_sentiment(text: str):
    """Predict sentiment for customer feedback."""

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Feedback text cannot be empty.")

    model = load_sentiment_model()

    sentiment = model.predict([text])[0]

    probabilities = model.predict_proba([text])[0]
    confidence = float(max(probabilities))

    return {
        "sentiment": sentiment,
        "confidence": round(confidence, 4)
    }
