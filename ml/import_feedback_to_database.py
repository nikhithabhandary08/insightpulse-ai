
from pathlib import Path

import pandas as pd

from app.db.database import SessionLocal
from app.models.customer import Customer
from app.models.product import Product
from app.models.channel import Channel
from app.models.review import Review
from app.models.theme import Theme


BASE_DIR = Path(__file__).resolve().parents[1]

CLEANED_DATA_PATH = (
    BASE_DIR / "data" / "generated" / "cleaned_customer_reviews.csv"
)

THEME_RESULTS_PATH = (
    BASE_DIR / "data" / "generated" / "theme_detection_results.csv"
)

CUSTOMER_ID = "CUS-KAGGLE-ANON"
CHANNEL_ID = "CH-001"


def import_feedback():
    print("Loading datasets...")

    if not CLEANED_DATA_PATH.exists():
        raise FileNotFoundError(CLEANED_DATA_PATH)

    if not THEME_RESULTS_PATH.exists():
        raise FileNotFoundError(THEME_RESULTS_PATH)

    reviews_df = pd.read_csv(CLEANED_DATA_PATH)
    themes_df = pd.read_csv(THEME_RESULTS_PATH)

    # Match theme results with the original review information.
    data = reviews_df.merge(
        themes_df[["text", "topic_id", "theme_name"]],
        on="text",
        how="left",
        validate="one_to_one"
    )

    if data["topic_id"].isna().any():
        raise ValueError("Some reviews do not have matching theme results.")

    print("Reviews ready for import:", len(data))

    db = SessionLocal()

    try:
        # Create the anonymous dataset customer.
        customer = db.query(Customer).filter(
            Customer.customer_id == CUSTOMER_ID
        ).first()

        if not customer:
            db.add(
                Customer(
                    customer_id=CUSTOMER_ID,
                    customer_name="Anonymous Dataset Customer",
                    email=None,
                    country=None
                )
            )
            db.flush()

        # Ensure the review channel exists.
        channel = db.query(Channel).filter(
            Channel.channel_id == CHANNEL_ID
        ).first()

        if not channel:
            db.add(
                Channel(
                    channel_id=CHANNEL_ID,
                    channel_name="Online Reviews",
                    description="Online customer reviews used for feedback analysis."
                )
            )
            db.flush()

        # Create product records using actual Clothing IDs.
        product_data = data[
            ["clothing_id", "product_class", "department"]
        ].drop_duplicates(subset=["clothing_id"])

        existing_product_ids = {
            row[0] for row in db.query(Product.product_id).all()
        }

        new_products = []

        for row in product_data.itertuples(index=False):
            if pd.isna(row.clothing_id):
                product_id = "PROD-KAGGLE-UNKNOWN"
                product_name = "Uncategorized Clothing Item"
            else:
                clothing_id = int(row.clothing_id)
                product_id = f"PROD-KAGGLE-{clothing_id}"
                product_name = f"Clothing Item {clothing_id}"

            if product_id in existing_product_ids:
                continue

            category = (
                str(row.product_class)
                if pd.notna(row.product_class)
                else "Uncategorized"
            )

            department = (
                str(row.department)
                if pd.notna(row.department)
                else "Uncategorized"
            )

            new_products.append(
                Product(
                    product_id=product_id,
                    product_name=product_name,
                    category=category,
                    description=f"Department: {department}. Source: Kaggle clothing reviews."
                )
            )

            existing_product_ids.add(product_id)

        db.add_all(new_products)
        db.flush()

        print("New products created:", len(new_products))

        # Create themes discovered by BERTopic.
        existing_themes = db.query(Theme).all()

        theme_id_by_name = {
            theme.theme_name: theme.theme_id
            for theme in existing_themes
        }

        existing_theme_ids = {
            theme.theme_id for theme in existing_themes
        }

        topic_to_theme_id = {}
        new_themes = []

        topic_data = (
            data[data["topic_id"] != -1][
                ["topic_id", "theme_name"]
            ]
            .drop_duplicates()
            .sort_values("topic_id")
        )

        for row in topic_data.itertuples(index=False):
            topic_id = int(row.topic_id)
            theme_name = str(row.theme_name)

            if theme_name in theme_id_by_name:
                topic_to_theme_id[topic_id] = theme_id_by_name[theme_name]
                continue

            theme_id = f"THEME-BERTOPIC-{topic_id:03d}"

            if theme_id in existing_theme_ids:
                raise ValueError(
                    f"Theme ID conflict: {theme_id}"
                )

            new_themes.append(
                Theme(
                    theme_id=theme_id,
                    theme_name=theme_name,
                    description=(
                        f"Automatically discovered by BERTopic. "
                        f"Original topic ID: {topic_id}."
                    )
                )
            )

            topic_to_theme_id[topic_id] = theme_id
            existing_theme_ids.add(theme_id)
            theme_id_by_name[theme_name] = theme_id

        db.add_all(new_themes)
        db.flush()

        print("New themes created:", len(new_themes))

        # Import reviews without duplicating existing records.
        existing_review_ids = {
            row[0] for row in db.query(Review.review_id).all()
        }

        new_reviews = []

        for index, row in enumerate(data.itertuples(index=False), start=1):
            review_id = f"REV-KAGGLE-{index:06d}"

            if review_id in existing_review_ids:
                continue

            clothing_id = (
                int(row.clothing_id)
                if pd.notna(row.clothing_id)
                else None
            )

            product_id = (
                f"PROD-KAGGLE-{clothing_id}"
                if clothing_id is not None
                else "PROD-KAGGLE-UNKNOWN"
            )

            topic_id = int(row.topic_id)

            theme_id = (
                topic_to_theme_id.get(topic_id)
                if topic_id != -1
                else None
            )

            new_reviews.append(
                Review(
                    review_id=review_id,
                    customer_id=CUSTOMER_ID,
                    product_id=product_id,
                    channel_id=CHANNEL_ID,
                    review_text=str(row.text),
                    sentiment=str(row.sentiment),
                    sentiment_confidence=None,
                    theme_id=theme_id
                )
            )

        db.add_all(new_reviews)
        db.commit()

        print("\nDatabase import completed successfully!")
        print("New reviews imported:", len(new_reviews))
        print("Existing reviews preserved:", len(existing_review_ids))
        print("Unassigned theme reviews:", (data["topic_id"] == -1).sum())

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    import_feedback()
