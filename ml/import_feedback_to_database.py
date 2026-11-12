import argparse
import csv
from datetime import datetime
from pathlib import Path

from app.db.database import SessionLocal
from app.models.customer import Customer
from app.models.product import Product
from app.models.channel import Channel
from app.models.survey import Survey
from app.models.survey_response import SurveyResponse
from app.models.review import Review
from app.models.support_message import SupportMessage
from app.models.theme import Theme
from app.models.sentiment_label import SentimentLabel
from app.models.action_item import ActionItem


BASE_DIR = Path(__file__).resolve().parents[1]
def parse_args():
    parser = argparse.ArgumentParser(
        description="Import InsightPulse AI synthetic data into SQLite."
    )
    parser.add_argument(
        "--scale",
        choices=["starter", "full"],
        default="starter",
        help="Dataset scale to import."
    )
    return parser.parse_args()


args = parse_args()

if args.scale == "full":
    GENERATED_DIR = BASE_DIR / "data" / "generated_full"
else:
    GENERATED_DIR = BASE_DIR / "data" / "generated"
def read_csv(filename):
    path = GENERATED_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Required generated file not found: {path}\n"
            "Run the synthetic data generator first."
        )

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def parse_datetime(value):
    if not value:
        return None
    return datetime.fromisoformat(value)


def existing_ids(db, model, id_column):
    return {row[0] for row in db.query(id_column).all()}


def add_missing_masters(db, rows, model, id_field, mapper):
    known_ids = existing_ids(db, model, getattr(model, id_field))
    objects = []

    for row in rows:
        record_id = row[id_field]

        if record_id in known_ids:
            continue

        objects.append(model(**mapper(row)))
        known_ids.add(record_id)

    if objects:
        db.add_all(objects)
        db.flush()

    return len(objects)


def add_missing_events(
    db,
    rows,
    model,
    id_field,
    mapper,
    batch_size=5000,
    model_id_field=None,
):
    """
    id_field: primary-key column in the CSV.
    model_id_field: corresponding primary-key field in the database model.
    """
    database_id_field = model_id_field or id_field

    known_ids = existing_ids(
        db,
        model,
        getattr(model, database_id_field)
    )

    inserted = 0
    batch = []

    for row in rows:
        record_id = row[id_field]

        if record_id in known_ids:
            continue

        batch.append(model(**mapper(row)))
        known_ids.add(record_id)

        if len(batch) >= batch_size:
            db.add_all(batch)
            db.flush()
            inserted += len(batch)
            batch.clear()

    if batch:
        db.add_all(batch)
        db.flush()
        inserted += len(batch)

    return inserted


def import_feedback():
    print("Loading generated synthetic CSV files...")

    customers = read_csv("customers.csv")
    products = read_csv("products.csv")
    channels = read_csv("channels.csv")
    surveys = read_csv("surveys.csv")
    themes = read_csv("themes.csv")
    sentiment_labels = read_csv("sentiment_labels.csv")

    reviews = read_csv("reviews.csv")
    responses = read_csv("survey_responses.csv")
    messages = read_csv("support_messages.csv")
    action_items = read_csv("action_items.csv")

    db = SessionLocal()
    inserted_counts = {}

    try:
        print("Importing master records...")

        inserted_counts["customers"] = add_missing_masters(
            db,
            customers,
            Customer,
            "customer_id",
            lambda row: {
                "customer_id": row["customer_id"],
                "customer_name": row["customer_name"],
                "email": row.get("email") or None,
                "country": row.get("country") or None,
            },
        )

        inserted_counts["products"] = add_missing_masters(
            db,
            products,
            Product,
            "product_id",
            lambda row: {
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "category": row["category"],
                "description": row.get("description") or None,
            },
        )

        inserted_counts["channels"] = add_missing_masters(
            db,
            channels,
            Channel,
            "channel_id",
            lambda row: {
                "channel_id": row["channel_id"],
                "channel_name": row["channel_name"],
                "description": row.get("description") or None,
            },
        )

        inserted_counts["surveys"] = add_missing_masters(
            db,
            surveys,
            Survey,
            "survey_id",
            lambda row: {
                "survey_id": row["survey_id"],
                "survey_title": (
                    row.get("survey_name")
                    or row.get("survey_title")
                    or row["survey_id"]
                ),
                "description": row.get("description") or None,
                "status": row.get("status") or "Active",
            },
        )

        inserted_counts["themes"] = add_missing_masters(
            db,
            themes,
            Theme,
            "theme_id",
            lambda row: {
                "theme_id": row["theme_id"],
                "theme_name": row["theme_name"],
                "description": row.get("description") or None,
            },
        )

        inserted_counts["sentiment_labels"] = add_missing_masters(
            db,
            sentiment_labels,
            SentimentLabel,
            "sentiment_id",
            lambda row: {
                "sentiment_id": row["sentiment_id"],
                "sentiment_name": row["sentiment_name"],
                "description": row.get("description") or None,
            },
        )

        db.flush()

        print("Importing feedback records...")

        inserted_counts["reviews"] = add_missing_events(
            db,
            reviews,
            Review,
            "review_id",
            lambda row: {
                "review_id": row["review_id"],
                "customer_id": row["customer_id"],
                "product_id": row["product_id"],
                "channel_id": row["channel_id"],
                "review_text": row["review_text"],
                "rating": int(row["rating"]) if row.get("rating") else None,
                "sentiment": row.get("sentiment") or None,
                "sentiment_confidence": (
                    float(row["sentiment_confidence"])
                    if row.get("sentiment_confidence")
                    else None
                ),
                "theme_id": row.get("theme_id") or None,
                "predicted_theme": row.get("predicted_theme") or None,
                "created_at": parse_datetime(row.get("created_at")),
            },
        )

        inserted_counts["survey_responses"] = add_missing_events(
            db,
            responses,
            SurveyResponse,
            "response_id",
            lambda row: {
                "response_id": row["response_id"],
                "survey_id": row["survey_id"],
                "customer_id": row["customer_id"],
                "product_id": row["product_id"],
                "channel_id": row["channel_id"],
                "response_text": row["response_text"],
                "sentiment": row.get("sentiment") or None,
                "sentiment_confidence": (
                    float(row["sentiment_confidence"])
                    if row.get("sentiment_confidence")
                    else None
                ),
                "theme_id": row.get("theme_id") or None,
                "predicted_theme": row.get("predicted_theme") or None,
                "submitted_at": parse_datetime(row.get("submitted_at")),
            },
        )

        inserted_counts["support_messages"] = add_missing_events(
            db,
            messages,
            SupportMessage,
            "message_id",
            lambda row: {
                "message_id": row["message_id"],
                "ticket_id": row["ticket_id"],
                "customer_id": row["customer_id"],
                "channel_id": row["channel_id"],
                "message_text": row["message_text"],
                "sentiment": row.get("sentiment") or None,
                "sentiment_confidence": (
                    float(row["sentiment_confidence"])
                    if row.get("sentiment_confidence")
                    else None
                ),
                "theme_id": row.get("theme_id") or None,
                "predicted_theme": row.get("predicted_theme") or None,
                "created_at": parse_datetime(row.get("created_at")),
            },
        )

        # CSV uses action_item_id; database model uses action_id.
        inserted_counts["action_items"] = add_missing_events(
            db,
            action_items,
            ActionItem,
            "action_item_id",
            lambda row: {
                "action_id": row["action_item_id"],
                "theme_id": row["theme_id"],
                "action_title": row["title"],
                "description": row["description"],
                "priority": row["priority"],
                "status": row["status"],
                "source_count": int(row["source_count"]),
                "negative_percentage": float(row["negative_percentage"]),
                "threshold_percentage": float(row["threshold_percentage"]),
            },
            model_id_field="action_id",
        )

        db.commit()

        print("\nSynthetic data import completed successfully.")
        print("New records inserted:")

        for table_name, count in inserted_counts.items():
            print(f"  {table_name}: {count}")

        print("\nExisting records with matching IDs were skipped.")
        print(
            "The intentionally duplicated survey submission was retained "
            "because it has its own response_id."
        )
        print(
            'The invalid predicted_theme value "Billing" was preserved '
            "for anomaly detection."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    import_feedback()
