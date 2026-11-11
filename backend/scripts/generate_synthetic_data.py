
import argparse
import csv
import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path


# =========================================================
# 1. CONFIGURATION
# =========================================================

SEED = 20261022

BASE_DIR = Path(__file__).resolve().parents[2]

GENERATED_DIR = BASE_DIR / "data" / "generated"
GROUND_TRUTH_DIR = BASE_DIR / "data" / "ground_truth"
MANIFEST_DIR = BASE_DIR / "data" / "manifests"

THEMES = [
    "Performance",
    "Customer Support",
    "Feature Request",
]

SENTIMENTS = [
    "Positive",
    "Neutral",
    "Negative",
    "Mixed",
]

PRODUCTS = [
    ("PRD-001", "Insight Mobile App", "Software"),
    ("PRD-002", "Insight Web Platform", "Software"),
    ("PRD-003", "Smart Analytics Device", "Hardware"),
    ("PRD-004", "Customer Portal", "Software"),
    ("PRD-005", "Payment Gateway", "Services"),
]

CHANNELS = [
    ("CH-001", "Website"),
    ("CH-002", "Mobile App"),
    ("CH-003", "Email"),
    ("CH-004", "Phone"),
    ("CH-005", "Social Media"),
]

THEME_TEXT = {
    "Performance": {
        "Positive": [
            "The application is fast and performs smoothly.",
            "Loading speed has improved significantly.",
            "The system works perfectly without delays.",
        ],
        "Neutral": [
            "The application performance is acceptable.",
            "The system is operating normally.",
            "The loading speed is average.",
        ],
        "Negative": [
            "The application is slow and frequently crashes.",
            "Loading takes too long and the system freezes.",
            "The dashboard is extremely slow.",
        ],
        "Mixed": [
            "The application is fast sometimes, but crashes often.",
            "The latest update improved speed but introduced errors.",
            "The system works well, but loading is inconsistent.",
        ],
    },
    "Customer Support": {
        "Positive": [
            "The support team resolved my problem quickly.",
            "Customer service was helpful and professional.",
            "The support agent was very understanding.",
        ],
        "Neutral": [
            "I received a response from customer support.",
            "The support ticket is currently being reviewed.",
            "The team acknowledged my request.",
        ],
        "Negative": [
            "Customer support has not resolved my issue.",
            "I waited several days without receiving assistance.",
            "Nobody responded to my support request.",
        ],
        "Mixed": [
            "The support agent was helpful, but the resolution was delayed.",
            "Support responded quickly but did not solve the issue.",
            "The agent was polite, but my problem remains unresolved.",
        ],
    },
    "Feature Request": {
        "Positive": [
            "The new features are useful and easy to understand.",
            "I appreciate the improvements to the application.",
            "The latest feature makes my work easier.",
        ],
        "Neutral": [
            "I would like to know more about the available features.",
            "The feature is currently available in the application.",
            "I am reviewing the new functionality.",
        ],
        "Negative": [
            "The application is missing important features.",
            "I cannot find the feature that I need.",
            "The application lacks useful customization options.",
        ],
        "Mixed": [
            "The new feature is useful, but it needs more options.",
            "I like the update, although some features are missing.",
            "The feature is helpful, but it could be improved.",
        ],
    },
}

MULTILINGUAL_TEXT = [
    "App chennagide, but sometimes it is very slow.",
    "Service is good, lekin payment failed yesterday.",
    "ಬಹಳ ಚೆನ್ನಾಗಿದೆ, but customer support needs improvement.",
    "La aplicación funciona bien, but loading takes too long.",
    "The support team helped me, ಧನ್ಯವಾದಗಳು.",
]

AMBIGUOUS_TEXT = [
    "Wow, another update that makes everything slower. Amazing!",
    "Great, I have to contact support for the third time.",
    "It works... when it wants to.",
    "Not bad, but definitely not impressive.",
]

PII_EXAMPLE = (
    "Please contact me at test.person@example.com "
    "because my account issue is unresolved."
)


# =========================================================
# 2. FILE HELPERS
# =========================================================

def write_csv(filename, rows):
    if not rows:
        return

    path = GENERATED_DIR / filename

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


def calculate_checksum(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def random_date(rng):
    start = datetime(2025, 1, 1)
    end = datetime(2026, 10, 31)

    days = (end - start).days

    result = start + timedelta(
        days=rng.randint(0, days)
    )

    return result.strftime("%Y-%m-%dT%H:%M:%S")


# =========================================================
# 3. MASTER TABLE GENERATION
# =========================================================

def generate_masters(rng, customer_count, survey_count):

    customers = []

    for i in range(1, customer_count + 1):
        customers.append({
            "customer_id": f"CUS-{i:06d}",
            "customer_name": f"Synthetic Customer {i:06d}",
            "email": f"customer{i:06d}@example.com",
            "created_at": random_date(rng),
        })

    products = [
        {
            "product_id": product_id,
            "product_name": name,
            "category": category,
        }
        for product_id, name, category in PRODUCTS
    ]

    channels = [
        {
            "channel_id": channel_id,
            "channel_name": name,
        }
        for channel_id, name in CHANNELS
    ]

    surveys = []

    for i in range(1, survey_count + 1):
        surveys.append({
            "survey_id": f"SUR-2026-{i:06d}",
            "survey_name": f"Customer Experience Survey {i:04d}",
            "start_date": "2026-01-01",
            "status": "Active",
        })

    themes = [
        {
            "theme_id": f"THEME-{i:06d}",
            "theme_name": theme,
            "description": f"Feedback related to {theme.lower()}",
        }
        for i, theme in enumerate(THEMES, start=1)
    ]

    sentiment_labels = [
        {
            "sentiment_id": f"SENT-{i:03d}",
            "sentiment_name": sentiment,
        }
        for i, sentiment in enumerate(SENTIMENTS, start=1)
    ]

    return (
        customers,
        products,
        channels,
        surveys,
        themes,
        sentiment_labels,
    )


# =========================================================
# 4. FEEDBACK TEXT GENERATION
# =========================================================

def choose_text(rng, theme, sentiment, index):

    if index % 97 == 0:
        return rng.choice(MULTILINGUAL_TEXT)

    if index % 113 == 0:
        return rng.choice(AMBIGUOUS_TEXT)

    return rng.choice(
        THEME_TEXT[theme][sentiment]
    )


def choose_rating(rng, sentiment):

    if sentiment == "Positive":
        return rng.randint(4, 5)

    if sentiment == "Negative":
        return rng.randint(1, 2)

    if sentiment == "Neutral":
        return 3

    return rng.choice([2, 3, 4])


# =========================================================
# 5. REVIEW AND SURVEY RESPONSE GENERATION
# =========================================================

def generate_feedback_rows(
    rng,
    count,
    record_type,
    customers,
    surveys,
    index_offset=0
):

    rows = []

    customer_ids = [
        customer["customer_id"]
        for customer in customers
    ]

    # PRODUCTS and CHANNELS contain tuples.
    # Extract their first elements for foreign keys.
    product_ids = [
        product[0]
        for product in PRODUCTS
    ]

    channel_ids = [
        channel[0]
        for channel in CHANNELS
    ]

    survey_ids = [
        survey["survey_id"]
        for survey in surveys
    ]

    for index in range(1, count + 1):

        global_index = index + index_offset

        # Balanced sentiment and theme distribution.
        sentiment = SENTIMENTS[
            (index - 1) % len(SENTIMENTS)
        ]

        theme = THEMES[
            (index - 1) % len(THEMES)
        ]

        text = choose_text(
            rng,
            theme,
            sentiment,
            global_index
        )

        created_at = random_date(rng)

        common = {
            "customer_id": rng.choice(customer_ids),
            "product_id": rng.choice(product_ids),
            "channel_id": rng.choice(channel_ids),
            "sentiment": sentiment,
            "sentiment_confidence": round(
                rng.uniform(0.75, 0.99), 3
            ),
            "theme_id": (
                f"THEME-{THEMES.index(theme) + 1:06d}"
            ),
            "predicted_theme": theme,
            "created_at": created_at,
            "feedback_text": text,
        }

        if record_type == "review":

            row = {
                "review_id": f"REV-2026-{index:06d}",
                **common,
                "review_text": text,
                "rating": choose_rating(rng, sentiment),
            }

        else:

            survey_id = survey_ids[
                (index - 1) % len(survey_ids)
            ]

            response_number = (
                (index - 1) // len(survey_ids)
            ) + 1

            row = {
                "response_id": (
                    f"RESP-{survey_id}-{response_number:03d}"
                ),
                "survey_id": survey_id,
                **common,
                "response_text": text,
                "submitted_at": created_at,
            }

        rows.append(row)

    return rows


# =========================================================
# 6. SUPPORT MESSAGE GENERATION
# =========================================================

def generate_support_messages(rng, count, customers):

    rows = []

    customer_ids = [
        customer["customer_id"]
        for customer in customers
    ]

    channel_ids = [
        channel[0]
        for channel in CHANNELS
    ]

    for index in range(1, count + 1):

        sentiment = SENTIMENTS[
            (index - 1) % len(SENTIMENTS)
        ]

        theme = THEMES[
            (index - 1) % len(THEMES)
        ]

        ticket_number = ((index - 1) // 4) + 1
        message_number = ((index - 1) % 4) + 1

        ticket_id = f"TKT-2026-{ticket_number:06d}"

        message_id = (
            f"MSG-{ticket_id}-{message_number:03d}"
        )

        text = choose_text(
            rng,
            theme,
            sentiment,
            index
        )

        rows.append({
            "message_id": message_id,
            "ticket_id": ticket_id,
            "customer_id": rng.choice(customer_ids),
            "channel_id": rng.choice(channel_ids),
            "message_text": text,
            "sentiment": sentiment,
            "sentiment_confidence": round(
                rng.uniform(0.75, 0.99), 3
            ),
            "theme_id": (
                f"THEME-{THEMES.index(theme) + 1:06d}"
            ),
            "predicted_theme": theme,
            "created_at": random_date(rng),
        })

    return rows


# =========================================================
# 7. ACTION ITEM GENERATION
# =========================================================

def generate_action_items(reviews, responses, messages):

    all_feedback = reviews + responses + messages

    action_items = []

    for index, theme in enumerate(THEMES, start=1):

        matching = [
            row for row in all_feedback
            if row["predicted_theme"] == theme
        ]

        negative_count = sum(
            1
            for row in matching
            if row["sentiment"] == "Negative"
        )

        total = len(matching)

        negative_percentage = (
            negative_count / total * 100
            if total else 0
        )

        threshold = 15.0

        if negative_percentage > threshold:
            priority = "High"
        elif negative_percentage > 10:
            priority = "Medium"
        else:
            priority = "Low"

        action_items.append({
            "action_item_id": f"ACT-{index:06d}",
            "theme_id": f"THEME-{index:06d}",
            "title": f"Investigate {theme} feedback",
            "description": (
                f"Review {negative_count} negative records "
                f"out of {total} records."
            ),
            "source_count": total,
            "negative_percentage": round(
                negative_percentage, 2
            ),
            "threshold_percentage": threshold,
            "priority": priority,
            "status": "Open",
        })

    return action_items


# =========================================================
# 8. EDGE CASE INJECTION
# =========================================================

def inject_edge_cases(reviews, responses, messages):

    ground_truth = []

    # -----------------------------------------------------
    # CASE 1: Sentiment contradicts feedback text
    # -----------------------------------------------------

    row = reviews[0]

    row["review_text"] = (
        "The application is terrible, slow and keeps crashing."
    )

    row["feedback_text"] = row["review_text"]
    row["sentiment"] = "Positive"

    ground_truth.append({
        "record_id": row["review_id"],
        "record_type": "Review",
        "issue_type": "Label contradicts text",
        "expected_decision": "Flag sentiment mismatch",
        "expected_sentiment": "Negative",
    })

    # -----------------------------------------------------
    # CASE 2: Duplicate survey response
    # -----------------------------------------------------

    original = responses[0]

    duplicate = original.copy()

    survey_id = original["survey_id"]

    # Keep the required response ID format.
    existing_numbers = []

    for response in responses:
        if response["survey_id"] == survey_id:
            response_id = response["response_id"]
            existing_numbers.append(
                int(response_id.rsplit("-", 1)[1])
            )

    next_number = max(existing_numbers) + 1

    duplicate["response_id"] = (
        f"RESP-{survey_id}-{next_number:03d}"
    )

    # All submission fields remain the same.
    # Only the immutable primary ID is different.
    responses.append(duplicate)

    ground_truth.append({
        "record_id": duplicate["response_id"],
        "record_type": "SurveyResponse",
        "issue_type": "Duplicate response",
        "expected_decision": "Flag duplicate submission",
        "duplicate_of": original["response_id"],
    })

    # -----------------------------------------------------
    # CASE 3: Synthetic PII in feedback
    # -----------------------------------------------------

    row = messages[0]

    row["message_text"] = PII_EXAMPLE

    ground_truth.append({
        "record_id": row["message_id"],
        "record_type": "SupportMessage",
        "issue_type": "PII leak",
        "expected_decision": "Flag email address in feedback",
        "synthetic_value": "test.person@example.com",
    })

    # -----------------------------------------------------
    # CASE 4: Theme outside allowed taxonomy
    # -----------------------------------------------------

    row = reviews[1]

    row["predicted_theme"] = "Billing"

    ground_truth.append({
        "record_id": row["review_id"],
        "record_type": "Review",
        "issue_type": "Out-of-taxonomy theme",
        "expected_decision": "Flag invalid theme",
        "invalid_theme": "Billing",
        "allowed_themes": THEMES,
    })

    # -----------------------------------------------------
    # CASE 5: Rating-text mismatch
    # -----------------------------------------------------

    row = reviews[2]

    row["rating"] = 5

    row["review_text"] = (
        "Very disappointed. The product does not work at all."
    )

    row["feedback_text"] = row["review_text"]

    ground_truth.append({
        "record_id": row["review_id"],
        "record_type": "Review",
        "issue_type": "Rating-text mismatch",
        "expected_decision": "Flag rating and text inconsistency",
        "rating": 5,
        "expected_sentiment": "Negative",
    })

    # -----------------------------------------------------
    # CASE 6: Test label leakage fixture
    # -----------------------------------------------------

    probe = [{
        "record_id": "LEAKAGE-PROBE-000001",
        "text": "The application is very slow and unreliable.",
        "test_label": "Negative",
    }]

    ground_truth.append({
        "record_id": "LEAKAGE-PROBE-000001",
        "record_type": "ModelInputProbe",
        "issue_type": "Test labels included in model input",
        "expected_decision": (
            "Detect and exclude test_label before feature extraction"
        ),
        "forbidden_feature": "test_label",
    })

    return ground_truth, probe


# =========================================================
# 9. DATA VALIDATION
# =========================================================

def validate_dataset(
    customers,
    products,
    channels,
    surveys,
    reviews,
    responses,
    messages
):

    errors = []

    customer_ids = {
        row["customer_id"] for row in customers
    }

    product_ids = {
        row["product_id"] for row in products
    }

    channel_ids = {
        row["channel_id"] for row in channels
    }

    survey_ids = {
        row["survey_id"] for row in surveys
    }

    review_ids = [
        row["review_id"] for row in reviews
    ]

    response_ids = [
        row["response_id"] for row in responses
    ]

    message_ids = [
        row["message_id"] for row in messages
    ]

    # Primary key checks.
    for name, values in [
        ("review_id", review_ids),
        ("response_id", response_ids),
        ("message_id", message_ids),
    ]:

        if len(values) != len(set(values)):
            errors.append(
                f"Duplicate primary key detected: {name}"
            )

    # Foreign key checks for reviews.
    for row in reviews:
        if row["customer_id"] not in customer_ids:
            errors.append("Invalid customer foreign key in reviews")

        if row["product_id"] not in product_ids:
            errors.append("Invalid product foreign key in reviews")

        if row["channel_id"] not in channel_ids:
            errors.append("Invalid channel foreign key in reviews")

    # Foreign key checks for survey responses.
    for row in responses:
        if row["customer_id"] not in customer_ids:
            errors.append("Invalid customer foreign key in responses")

        if row["product_id"] not in product_ids:
            errors.append("Invalid product foreign key in responses")

        if row["channel_id"] not in channel_ids:
            errors.append("Invalid channel foreign key in responses")

        if row["survey_id"] not in survey_ids:
            errors.append("Invalid survey foreign key in responses")

    # Foreign key checks for support messages.
    for row in messages:
        if row["customer_id"] not in customer_ids:
            errors.append("Invalid customer foreign key in messages")

        if row["channel_id"] not in channel_ids:
            errors.append("Invalid channel foreign key in messages")

    # Theme validation is intentionally not performed against
    # predicted_theme here because an invalid theme is an
    # injected anomaly that must be caught by the audit system.

    return errors


# =========================================================
# 10. MAIN GENERATOR
# =========================================================

def main():

    parser = argparse.ArgumentParser(
        description="Generate synthetic InsightPulse AI data"
    )

    parser.add_argument(
        "--scale",
        choices=["starter", "full"],
        default="starter",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
    )

    args = parser.parse_args()

    rng = random.Random(args.seed)

    # -----------------------------------------------------
    # Dataset sizes
    # -----------------------------------------------------

    if args.scale == "full":

        review_count = 30000
        response_count = 20000
        support_count = 20000

        customer_count = 5000
        survey_count = 100

    else:

        review_count = 300
        response_count = 200
        support_count = 200

        customer_count = 100
        survey_count = 5

    # -----------------------------------------------------
    # Create output directories
    # -----------------------------------------------------

    GENERATED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    GROUND_TRUTH_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    MANIFEST_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Generating InsightPulse AI synthetic data...")
    print(f"Scale: {args.scale}")
    print(f"Seed: {args.seed}")

    # -----------------------------------------------------
    # Generate master tables first
    # -----------------------------------------------------

    (
        customers,
        products,
        channels,
        surveys,
        themes,
        sentiment_labels,
    ) = generate_masters(
        rng,
        customer_count,
        survey_count
    )

    # -----------------------------------------------------
    # Generate feedback tables
    # -----------------------------------------------------

    reviews = generate_feedback_rows(
        rng,
        review_count,
        "review",
        customers,
        surveys
    )

    responses = generate_feedback_rows(
        rng,
        response_count,
        "survey",
        customers,
        surveys,
        index_offset=review_count
    )

    messages = generate_support_messages(
        rng,
        support_count,
        customers
    )

    # -----------------------------------------------------
    # Inject edge cases after baseline generation
    # -----------------------------------------------------

    ground_truth, leakage_probe = inject_edge_cases(
        reviews,
        responses,
        messages
    )

    # -----------------------------------------------------
    # Generate derived action items
    # -----------------------------------------------------

    action_items = generate_action_items(
        reviews,
        responses,
        messages
    )

    # -----------------------------------------------------
    # Export master tables
    # -----------------------------------------------------

    write_csv("customers.csv", customers)
    write_csv("products.csv", products)
    write_csv("channels.csv", channels)
    write_csv("surveys.csv", surveys)
    write_csv("themes.csv", themes)
    write_csv("sentiment_labels.csv", sentiment_labels)

    # -----------------------------------------------------
    # Export child/event tables
    # -----------------------------------------------------

    write_csv("reviews.csv", reviews)
    write_csv("survey_responses.csv", responses)
    write_csv("support_messages.csv", messages)
    write_csv("action_items.csv", action_items)

    # Deliberately contaminated test fixture.
    # This must never be used as production model input.
    write_csv(
        "model_input_adversarial.csv",
        leakage_probe
    )

    # -----------------------------------------------------
    # Export separate ground truth
    # -----------------------------------------------------

    write_json(
        GROUND_TRUTH_DIR / "ground_truth.json",
        {
            "seed": args.seed,
            "description": (
                "Synthetic evaluation cases. Never use this "
                "file as model input or training features."
            ),
            "cases": ground_truth,
        }
    )

    # -----------------------------------------------------
    # Validate generated data
    # -----------------------------------------------------

    validation_errors = validate_dataset(
        customers,
        products,
        channels,
        surveys,
        reviews,
        responses,
        messages
    )

    all_feedback = reviews + responses + messages

    sentiment_counts = Counter(
        row["sentiment"]
        for row in all_feedback
    )

    # -----------------------------------------------------
    # Validation summary
    # -----------------------------------------------------

    summary = {
        "scale": args.scale,
        "seed": args.seed,
        "generated_at": datetime.now().isoformat(),

        "row_counts": {
            "customers": len(customers),
            "products": len(products),
            "channels": len(channels),
            "surveys": len(surveys),
            "reviews": len(reviews),
            "survey_responses": len(responses),
            "support_messages": len(messages),
            "action_items": len(action_items),
        },

        "sentiment_counts": dict(sentiment_counts),

        "ground_truth_cases": len(ground_truth),

        "validation_errors": validation_errors,

        "validation_status": (
            "PASSED"
            if not validation_errors
            else "FAILED"
        ),
    }

    write_json(
        MANIFEST_DIR / "validation_summary.json",
        summary
    )

    # -----------------------------------------------------
    # Source manifest and checksums
    # -----------------------------------------------------

    manifest = {
        "project": "InsightPulse AI",
        "generator": (
            "backend/scripts/generate_synthetic_data.py"
        ),
        "seed": args.seed,
        "scale": args.scale,
        "synthetic_data_only": True,
        "files": {},
    }

    for path in sorted(GENERATED_DIR.glob("*.csv")):

        manifest["files"][path.name] = {
            "sha256": calculate_checksum(path),
            "size_bytes": path.stat().st_size,
        }

    write_json(
        MANIFEST_DIR / "source_manifest.json",
        manifest
    )

    # -----------------------------------------------------
    # Final output
    # -----------------------------------------------------

    print("\nGeneration completed.")

    print(
        json.dumps(
            summary,
            indent=2
        )
    )

    if validation_errors:
        raise SystemExit(
            "Dataset validation failed. Check the errors above."
        )

    print(
        "\nSynthetic data generation and baseline "
        "validation passed."
    )


if __name__ == "__main__":
    main()
