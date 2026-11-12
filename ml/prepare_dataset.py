
import json
from pathlib import Path

import pandas as pd


# ==========================================
# PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = (
    BASE_DIR / "data" / "generated_full" / "reviews.csv"
)

PROCESSED_DATA_PATH = (
    BASE_DIR / "data" / "generated_full" / "cleaned_reviews.csv"
)

GROUND_TRUTH_PATH = (
    BASE_DIR / "data" / "ground_truth_full" / "ground_truth.json"
)

REQUIRED_SENTIMENTS = {
    "Positive",
    "Neutral",
    "Negative",
    "Mixed",
}


# ==========================================
# PREPARE SENTIMENT TRAINING DATASET
# ==========================================

def prepare_dataset():

    print("Loading synthetic customer reviews...")

    # Check input dataset
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_DATA_PATH}"
        )

    # Check ground-truth file
    if not GROUND_TRUTH_PATH.exists():
        raise FileNotFoundError(
            f"Ground-truth file not found: {GROUND_TRUTH_PATH}"
        )

    # Load raw reviews
    df = pd.read_csv(RAW_DATA_PATH)

    original_row_count = len(df)

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

    # ==========================================
    # LOAD GROUND-TRUTH EVALUATION RECORDS
    # ==========================================

    with open(
        GROUND_TRUTH_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        ground_truth = json.load(file)

    ground_truth_review_ids = {
        case["record_id"]
        for case in ground_truth.get("cases", [])
        if case.get("record_type") == "Review"
        and case.get("record_id")
    }

    print(
        "\nGround-truth review records identified:",
        len(ground_truth_review_ids)
    )

    # ==========================================
    # SELECT REQUIRED TRAINING COLUMNS
    # ==========================================

    # Keep only the fields required for sentiment training.
    df = df[
        ["review_id", "review_text", "sentiment"]
    ].copy()

    # ==========================================
    # DATA CLEANING
    # ==========================================

    df = df.dropna(
        subset=["review_text", "sentiment"]
    ).copy()

    df["review_text"] = (
        df["review_text"]
        .astype(str)
        .str.strip()
    )

    df["sentiment"] = (
        df["sentiment"]
        .astype(str)
        .str.strip()
    )

    df["review_id"] = df["review_id"].astype(str)

    # Remove empty text
    df = df[
        df["review_text"] != ""
    ].copy()

    # ==========================================
    # EXCLUDE GROUND-TRUTH RECORDS
    # ==========================================

    before_exclusion = len(df)

    df = df[
        ~df["review_id"].isin(ground_truth_review_ids)
    ].copy()

    excluded_count = before_exclusion - len(df)

    print(
        "Ground-truth review records excluded:",
        excluded_count
    )

    # ==========================================
    # REMOVE CONFLICTING SENTIMENT LABELS
    # ==========================================

    label_counts = (
        df.groupby("review_text")["sentiment"]
        .nunique()
    )

    conflicting_texts = label_counts[
        label_counts > 1
    ].index

    conflicting_count = len(conflicting_texts)

    df = df[
        ~df["review_text"].isin(conflicting_texts)
    ].copy()

    print(
        "Conflicting text examples removed:",
        conflicting_count
    )

    # ==========================================
    # REMOVE DUPLICATE SENTENCES
    # ==========================================

    before_deduplication = len(df)

    df = df.drop_duplicates(
        subset=["review_text"]
    ).copy()

    duplicates_removed = (
        before_deduplication - len(df)
    )

    print(
        "Duplicate sentences removed:",
        duplicates_removed
    )

    # ==========================================
    # VALIDATE SENTIMENT CLASSES
    # ==========================================

    actual_sentiments = set(
        df["sentiment"].unique()
    )

    if actual_sentiments != REQUIRED_SENTIMENTS:
        raise ValueError(
            "Unexpected sentiment labels. "
            f"Expected: {sorted(REQUIRED_SENTIMENTS)}, "
            f"Found: {sorted(actual_sentiments)}"
        )

    # ==========================================
    # FINAL TRAINING DATASET
    # ==========================================

    df = df.rename(
        columns={
            "review_text": "text",
        }
    )

    df = df[
        ["review_id", "text", "sentiment"]
    ]

    # Final ground-truth leakage check
    remaining_ground_truth_ids = (
        set(df["review_id"])
        & ground_truth_review_ids
    )

    if remaining_ground_truth_ids:
        raise ValueError(
            "Ground-truth leakage detected! "
            f"Remaining IDs: {sorted(remaining_ground_truth_ids)}"
        )

    # ==========================================
    # SAVE PROCESSED DATASET
    # ==========================================

    PROCESSED_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        PROCESSED_DATA_PATH,
        index=False
    )

    # ==========================================
    # SUMMARY
    # ==========================================

    print("\n======================================")
    print("DATASET PREPARATION COMPLETED")
    print("======================================")

    print(f"Original input rows: {original_row_count}")
    print(f"Prepared unique examples: {len(df)}")
    print(f"Ground-truth records excluded: {excluded_count}")
    print(f"Duplicate sentences removed: {duplicates_removed}")
    print(f"Output file: {PROCESSED_DATA_PATH}")

    print("\nSentiment distribution:")

    print(
        df["sentiment"]
        .value_counts()
        .sort_index()
    )

    print("\nGround-truth leakage check: PASSED")


# ==========================================
# RUN DATASET PREPARATION
# ==========================================

if __name__ == "__main__":
    prepare_dataset()
