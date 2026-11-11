
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "customer_reviews.csv"
PROCESSED_DATA_PATH = (
    BASE_DIR / "data" / "generated" / "cleaned_customer_reviews.csv"
)


def prepare_dataset():
    print("Loading customer review dataset...")

    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {RAW_DATA_PATH}")

    df = pd.read_csv(RAW_DATA_PATH)

    required_columns = [
        "Review Text",
        "Rating",
        "Clothing ID",
        "Department Name",
        "Class Name",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing dataset columns: {missing_columns}")

    # Preserve review text, rating, and original product information.
    df = df[required_columns].copy()

    # Remove missing or empty review text.
    df = df.dropna(subset=["Review Text"])
    df["Review Text"] = df["Review Text"].astype(str).str.strip()
    df = df[df["Review Text"] != ""]

    # Remove duplicate reviews.
    df = df.drop_duplicates(subset=["Review Text"]).copy()

    # Preserve missing product categories transparently.
    df["Department Name"] = df["Department Name"].fillna("Uncategorized")
    df["Class Name"] = df["Class Name"].fillna("Uncategorized")

    # Convert ratings into sentiment labels.
    def assign_sentiment(rating):
        if rating <= 2:
            return "negative"
        elif rating == 3:
            return "neutral"
        return "positive"

    df["sentiment"] = df["Rating"].apply(assign_sentiment)

    # Rename columns for application usage.
    df = df.rename(
        columns={
            "Review Text": "text",
            "Clothing ID": "clothing_id",
            "Department Name": "department",
            "Class Name": "product_class",
        }
    )

    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        PROCESSED_DATA_PATH,
        index=False,
        encoding="utf-8"
    )

    print("\nDataset preparation completed!")
    print("Total reviews:", len(df))

    print("\nSentiment distribution:")
    print(df["sentiment"].value_counts())

    print("\nProduct class distribution:")
    print(df["product_class"].value_counts())

    print("\nDepartment distribution:")
    print(df["department"].value_counts())

    print("\nFinal columns:")
    print(df.columns.tolist())

    print("\nSaved to:", PROCESSED_DATA_PATH)


if __name__ == "__main__":
    prepare_dataset()
