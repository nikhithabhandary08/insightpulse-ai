
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = (
    BASE_DIR / "data" / "generated_full" / "reviews.csv"
)

PROCESSED_DATA_PATH = (
    BASE_DIR / "data" / "generated_full" / "cleaned_reviews.csv"
)

REQUIRED_SENTIMENTS = {
    "Positive",
    "Neutral",
    "Negative",
    "Mixed",
}


def prepare_dataset():
    print("Loading synthetic customer reviews...")

    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_DATA_PATH}"
        )

    df = pd.read_csv(RAW_DATA_PATH)

    required_columns = {
        "review_id",
        "review_text",
        "sentiment",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Keep only the fields required for sentiment training.
    df = df[
        ["review_id", "review_text", "sentiment"]
    ].copy()

    df = df.dropna(
        subset=["review_text", "sentiment"]
    )

    df["review_text"] = (
        df["review_text"].astype(str).str.strip()
    )

    df["sentiment"] = (
        df["sentiment"].astype(str).str.strip()
    )

    df = df[df["review_text"] != ""]

    # Remove sentences assigned multiple sentiment labels.
    label_counts = (
        df.groupby("review_text")["sentiment"].nunique()
    )

    conflicting_texts = label_counts[
        label_counts > 1
    ].index

    df = df[
        ~df["review_text"].isin(conflicting_texts)
    ].copy()

    # Exclude the known injected sentiment contradiction.
    df = df[
        df["review_id"] != "REV-2026-000001"
    ].copy()

    # Keep one example per unique sentence.
    df = df.drop_duplicates(
        subset=["review_text"]
    ).copy()

    # Validate the four required sentiment classes.
    actual_sentiments = set(df["sentiment"].unique())

    if actual_sentiments != REQUIRED_SENTIMENTS:
        raise ValueError(
            f"Unexpected sentiment labels: {actual_sentiments}"
        )

    # Rename columns for the ML pipeline.
    df = df.rename(
        columns={
            "review_text": "text",
        }
    )

    df = df[["review_id", "text", "sentiment"]]

    PROCESSED_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        PROCESSED_DATA_PATH,
        index=False,
    )

    print("\nDataset preparation completed.")
    print(f"Original input rows: {len(pd.read_csv(RAW_DATA_PATH))}")
    print(f"Prepared unique examples: {len(df)}")
    print(f"Output: {PROCESSED_DATA_PATH}")

    print("\nSentiment distribution:")
    print(df["sentiment"].value_counts().sort_index())


if __name__ == "__main__":
    prepare_dataset()
