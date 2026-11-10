
from pathlib import Path

import pandas as pd


# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "customer_reviews.csv"
PROCESSED_DATA_PATH = (
    BASE_DIR / "data" / "generated" / "cleaned_customer_reviews.csv"
)


def prepare_dataset():
    print("Loading customer review dataset...")

    df = pd.read_csv(RAW_DATA_PATH)

    # Keep only the columns needed for sentiment analysis
    df = df[["Review Text", "Rating"]].copy()

    # Remove rows with missing or empty review text
    df = df.dropna(subset=["Review Text"])
    df["Review Text"] = df["Review Text"].astype(str).str.strip()
    df = df[df["Review Text"] != ""]

    # Remove duplicate reviews
    df = df.drop_duplicates(subset=["Review Text"])

    # Convert ratings into sentiment labels
    def assign_sentiment(rating):
        if rating <= 2:
            return "negative"
        elif rating == 3:
            return "neutral"
        else:
            return "positive"

    df["sentiment"] = df["Rating"].apply(assign_sentiment)

    # Rename columns
    df = df.rename(columns={"Review Text": "text"})

    # Save cleaned dataset
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)

    print("\nDataset preparation completed!")
    print(f"Total reviews: {len(df)}")
    print("\nSentiment distribution:")
    print(df["sentiment"].value_counts())

    print(f"\nCleaned dataset saved to:\n{PROCESSED_DATA_PATH}")


if __name__ == "__main__":
    prepare_dataset()
