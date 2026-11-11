
from pathlib import Path

import pandas as pd

from app.services.theme_service import (
    train_theme_model,
    get_theme_summary
)


# Project paths
BASE_DIR = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    BASE_DIR / "data" / "generated" / "cleaned_customer_reviews.csv"
)

OUTPUT_PATH = (
    BASE_DIR / "data" / "generated" / "theme_detection_results.csv"
)


def main():
    print("Loading customer reviews...")

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    # Validate required columns
    required_columns = ["text", "sentiment"]
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Keep valid customer feedback
    df = df.dropna(subset=["text"]).copy()
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"] != ""].reset_index(drop=True)

    feedback_texts = df["text"].tolist()

    print(f"Total reviews loaded: {len(feedback_texts)}")

    print("\nStarting BERTopic theme detection...")

    topic_model, documents, topics = train_theme_model(
        feedback_texts,
        min_topic_size=30
    )

    # Associate every review with its discovered topic
    results = pd.DataFrame({
        "text": documents,
        "sentiment": df["sentiment"].tolist(),
        "topic_id": topics
    })

    # Map topic IDs to meaningful topic names
    topic_names = {
        int(row["Topic"]): str(row["Name"])
        for _, row in topic_model.get_topic_info().iterrows()
    }

    results["theme_name"] = results["topic_id"].map(topic_names)

    # Standardize unassigned reviews
    results.loc[
        results["topic_id"] == -1,
        "theme_name"
    ] = "Unassigned"

    # Handle any unexpected missing theme names
    results["theme_name"] = results["theme_name"].fillna(
        "Unassigned"
    )

    # Save results
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    results.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8"
    )

    print("\nTheme detection completed!")

    print("\nDiscovered themes:")

    for theme in get_theme_summary(topic_model):
        print(theme)

    print("\nSentiment distribution:")
    print(results["sentiment"].value_counts())

    print("\nTheme distribution:")
    print(results["theme_name"].value_counts())

    print("\nTotal reviews processed:", len(results))

    print(
        "Unassigned reviews:",
        (results["topic_id"] == -1).sum()
    )

    print("\nResults saved to:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
