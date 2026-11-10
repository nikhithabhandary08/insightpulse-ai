
from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ==========================================
# PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "generated"
    / "cleaned_customer_reviews.csv"
)

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "sentiment_pipeline.joblib"
)


# ==========================================
# TRAIN SENTIMENT MODEL
# ==========================================

def train_sentiment_model():

    print("Loading customer review dataset...")

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Training dataset not found: {DATA_PATH}"
        )

    data = pd.read_csv(DATA_PATH)

    # Validate required columns
    required_columns = {"text", "sentiment"}

    if not required_columns.issubset(data.columns):
        raise ValueError(
            "Dataset must contain 'text' and 'sentiment' columns."
        )

    # Remove missing values
    data = data.dropna(subset=["text", "sentiment"]).copy()

    # Clean text and labels
    data["text"] = data["text"].astype(str).str.strip()

    data["sentiment"] = (
        data["sentiment"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    data = data[data["text"] != ""]

    print(f"Total reviews available: {len(data)}")

    print("\nSentiment distribution:")
    print(data["sentiment"].value_counts())

    # Check sentiment classes
    if data["sentiment"].nunique() < 2:
        raise ValueError(
            "At least two sentiment classes are required."
        )

    # Split dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        data["text"],
        data["sentiment"],
        test_size=0.2,
        random_state=42,
        stratify=data["sentiment"]
    )

    print("\nTraining reviews:", len(X_train))
    print("Testing reviews:", len(X_test))

    # Build ML pipeline
    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                stop_words=None,
                ngram_range=(1, 2),
                max_features=20000,
                sublinear_tf=True
            )
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42
            )
        )
    ])

    # Train model
    print("\nTraining sentiment model...")

    model.fit(X_train, y_train)

    # Evaluate model
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print("\n================================")
    print("SENTIMENT MODEL EVALUATION")
    print("================================")

    print(f"\nAccuracy: {accuracy:.4f}")

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    print("\nConfusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            predictions,
            labels=["negative", "neutral", "positive"]
        )
    )

    # Save trained model
    joblib.dump(model, MODEL_PATH)

    print("\n================================")
    print("MODEL TRAINING COMPLETED")
    print("================================")

    print(f"\nModel saved at: {MODEL_PATH}")

    return model


# ==========================================
# PREDICT SENTIMENT
# ==========================================

def predict_sentiment(text: str):

    if not isinstance(text, str) or not text.strip():
        raise ValueError(
            "Feedback text cannot be empty."
        )

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Trained model not found. "
            "Train the model first."
        )

    # Load trained model
    model = joblib.load(MODEL_PATH)

    # Predict sentiment
    prediction = model.predict([text])[0]

    # Calculate prediction confidence
    probabilities = model.predict_proba([text])[0]

    confidence = float(max(probabilities))

    return {
        "text": text,
        "sentiment": prediction,
        "confidence": round(confidence, 4)
    }


# ==========================================
# RUN TRAINING
# ==========================================

if __name__ == "__main__":

    train_sentiment_model()
