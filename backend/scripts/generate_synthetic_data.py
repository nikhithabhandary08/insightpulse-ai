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
            "The application loads quickly and runs smoothly.",
            "The latest update has significantly improved loading speed.",
            "The dashboard responds instantly to my requests.",
            "The system works reliably without unexpected delays.",
            "Pages open quickly and navigation feels smooth.",
            "The application performs better than before.",
            "I have experienced very few performance issues.",
            "The application responds quickly to every request.",
            "The system runs smoothly throughout the day.",
            "The improved performance makes daily tasks easier.",
            "The application is stable and consistently responsive.",
            "The system remains responsive even during busy periods.",
        ],
        "Neutral": [
            "The application takes a normal amount of time to load.",
            "The system performance is similar to last week.",
            "The dashboard displays the requested information.",
            "The application is functioning as expected.",
            "The application performance is acceptable.",
            "The system is operating normally.",
            "The loading speed is average.",
            "The dashboard takes a few seconds to respond.",
            "Performance has remained unchanged this month.",
            "The application works at its usual speed.",
            "The system completed the requested operation.",
            "I have not noticed any major performance changes.",
        ],
        "Negative": [
            "The application frequently becomes unresponsive.",
            "Slow response times interrupt my daily work.",
            "The system takes too long to process requests.",
            "Performance problems make the application frustrating to use.",
            "The application is slow and frequently crashes.",
            "Loading takes too long and the system freezes.",
            "The dashboard becomes extremely slow.",
            "Pages take several minutes to load.",
            "The application stops responding during normal use.",
            "The latest update has made performance worse.",
            "The system crashes whenever I open large reports.",
            "Frequent delays make the application difficult to use.",
        ],
        "Mixed": [
            "The application is generally fast, but some pages load slowly.",
            "The update improved stability, but performance remains inconsistent.",
            "The system responds quickly, although occasional crashes occur.",
            "The dashboard loads faster, but reports still take too long.",
            "The application loads quickly, but it crashes occasionally.",
            "The latest update improved speed but introduced errors.",
            "The system works well, although loading is inconsistent.",
            "Navigation is smooth, but some pages remain slow.",
            "Performance has improved, but unexpected freezes continue.",
            "The dashboard is faster, although it sometimes stops responding.",
            "The application works most of the time, but delays still occur.",
            "Loading is quicker now, but certain features remain unstable.",
        ],
    },
    "Customer Support": {
        "Positive": [
            "The support representative resolved my concern professionally.",
            "The team followed up and provided a satisfactory solution.",
            "The customer service experience was excellent.",
            "The support team handled my request efficiently.",
            "The support team resolved my problem quickly.",
            "Customer service was helpful and professional.",
            "The support agent understood my issue immediately.",
            "I received a clear solution from the support team.",
            "The representative was polite and very helpful.",
            "Customer support responded promptly and resolved my concern.",
            "The team provided excellent assistance throughout the process.",
            "My issue was resolved during the first conversation.",
        ],
        "Neutral": [
            "My request is awaiting a response from the support team.",
            "The support representative shared the ticket number.",
            "The team confirmed receipt of my complaint.",
            "My support case is currently under investigation.",
            "I received a response from customer support.",
            "The support ticket is currently being reviewed.",
            "The team acknowledged my request.",
            "My support request has been registered.",
            "The representative requested additional information.",
            "Customer support provided an update about my case.",
            "The ticket is still open.",
            "I am waiting for the next support update.",
        ],
        "Negative": [
            "The support team failed to address my complaint.",
            "I received no useful response from customer service.",
            "The support process was frustrating and time-consuming.",
            "My repeated requests have not received any attention.",
            "Customer support has not resolved my issue.",
            "I waited several days without receiving assistance.",
            "Nobody responded to my support request.",
            "The support team repeatedly ignored my messages.",
            "The representative could not provide a solution.",
            "My issue remains unresolved after several calls.",
            "I had to explain the same problem multiple times.",
            "The delayed response caused unnecessary frustration.",
        ],
        "Mixed": [
            "The agent was courteous, but the issue was not resolved.",
            "Support provided useful information, but the response arrived late.",
            "The team responded quickly, although the solution was incomplete.",
            "The representative was helpful, but I still need further assistance.",
            "The support agent was helpful, but the resolution was delayed.",
            "Support responded quickly but did not solve the issue.",
            "The representative was polite, but my problem remains unresolved.",
            "The team understood my concern, although no solution was provided.",
            "Customer service was friendly, but the waiting time was excessive.",
            "I received a quick response, but the instructions were unclear.",
            "The agent tried to help, but my issue happened again.",
            "The support experience was good, except for the delayed resolution.",
        ],
    },
    "Feature Request": {
        "Positive": [
            "The new functionality has made the application more convenient.",
            "The additional feature improves my daily workflow.",
            "The latest enhancement is useful and works reliably.",
            "The new options make the application more flexible.",
            "The new features are useful and easy to understand.",
            "I appreciate the improvements to the application.",
            "The latest feature makes my work easier.",
            "The new customization options are very helpful.",
            "The updated dashboard provides useful functionality.",
            "The additional filters make searching much easier.",
            "The new feature works exactly as expected.",
            "The application now provides the tools I need.",
        ],
        "Neutral": [
            "I would like to explore the additional application settings.",
            "The requested functionality is listed in the feature menu.",
            "The application currently supports several customization options.",
            "I have submitted a request for an additional feature.",
            "I would like to know more about the available features.",
            "The feature is currently available in the application.",
            "I am reviewing the new functionality.",
            "The application includes an additional reporting option.",
            "I have not tried the latest feature yet.",
            "The customization option is available in settings.",
            "The feature request has been recorded.",
            "I am considering using the new functionality.",
        ],
        "Negative": [
            "The application does not provide the functionality I require.",
            "The lack of customization makes the application difficult to use.",
            "The current features are insufficient for my workflow.",
            "I am disappointed that the requested functionality is unavailable.",
            "The application is missing important features.",
            "I cannot find the feature that I need.",
            "The application lacks useful customization options.",
            "The current reporting tools do not meet my requirements.",
            "The application needs better filtering options.",
            "I cannot complete my work without the requested feature.",
            "The available functionality is too limited.",
            "The missing export option makes reporting difficult.",
        ],
        "Mixed": [
            "The new feature is convenient, but its settings are limited.",
            "The update adds useful tools, although some improvements are still needed.",
            "The functionality is helpful, but the interface is confusing.",
            "The new option saves time, but it does not support every use case.",
            "The new feature is useful, but it needs more options.",
            "I like the update, although some features are missing.",
            "The feature is helpful, but it could be improved.",
            "The new dashboard looks good, but customization is limited.",
            "The additional filters help, but some search options are missing.",
            "The feature saves time, although it has a few limitations.",
            "The update is useful, but the navigation could be simpler.",
            "I appreciate the new functionality, but it needs more flexibility.",
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

DATA_START = datetime(2025, 1, 1)
DATA_END = datetime(2026, 10, 31)


# =========================================================
# 2. FILE HELPERS
# =========================================================

def write_csv(filename, rows):
    """Write a list of dictionaries to a CSV file."""
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
    """Write JSON with readable formatting and Unicode support."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


def calculate_checksum(path):
    """Calculate SHA-256 checksum for a generated file."""
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def random_date(rng, start=DATA_START, end=DATA_END):
    """Return a reproducible random ISO timestamp within a date range."""
    if start > end:
        raise ValueError("Date range start cannot be after end.")

    days = (end.date() - start.date()).days
    result = start + timedelta(days=rng.randint(0, days))

    return result.strftime("%Y-%m-%dT%H:%M:%S")


def parse_date(value, field_name, errors, record_id):
    """Parse an ISO date or timestamp and record a validation error."""
    try:
        return datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        errors.append(
            f"Invalid date in {field_name} for record {record_id}: {value}"
        )
        return None


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

    return rng.choice(THEME_TEXT[theme][sentiment])


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

    survey_start_dates = {
        survey["survey_id"]: datetime.fromisoformat(
            survey["start_date"]
        )
        for survey in surveys
    }

    for index in range(1, count + 1):
        global_index = index + index_offset

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

        survey_id = None

        if record_type == "survey":
            survey_id = survey_ids[
                (index - 1) % len(survey_ids)
            ]

            # Survey responses must not predate their survey.
            created_at = random_date(
                rng,
                start=survey_start_dates[survey_id],
                end=DATA_END
            )
        else:
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

        elif record_type == "survey":
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

        else:
            raise ValueError(
                "record_type must be 'review' or 'survey'."
            )

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

    # CASE 1: Sentiment contradicts feedback text.
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

    # CASE 2: Duplicate survey response with a distinct primary key.
    original = responses[0]
    duplicate = original.copy()
    survey_id = original["survey_id"]

    existing_numbers = [
        int(response["response_id"].rsplit("-", 1)[1])
        for response in responses
        if response["survey_id"] == survey_id
    ]

    next_number = max(existing_numbers) + 1

    duplicate["response_id"] = (
        f"RESP-{survey_id}-{next_number:03d}"
    )

    responses.append(duplicate)

    ground_truth.append({
        "record_id": duplicate["response_id"],
        "record_type": "SurveyResponse",
        "issue_type": "Duplicate response",
        "expected_decision": "Flag duplicate submission",
        "duplicate_of": original["response_id"],
    })

    # CASE 3: Synthetic PII in feedback.
    row = messages[0]
    row["message_text"] = PII_EXAMPLE

    ground_truth.append({
        "record_id": row["message_id"],
        "record_type": "SupportMessage",
        "issue_type": "PII leak",
        "expected_decision": "Flag email address in feedback",
        "synthetic_value": "test.person@example.com",
    })

    # CASE 4: Theme outside the approved taxonomy.
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

    # CASE 5: Rating-text mismatch.
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

    # CASE 6: Deliberately contaminated fixture for leakage testing.
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

    # Primary-key checks across every generated entity.
    primary_key_checks = [
        ("customer_id", customers),
        ("product_id", products),
        ("channel_id", channels),
        ("survey_id", surveys),
        ("review_id", reviews),
        ("response_id", responses),
        ("message_id", messages),
    ]

    for field, rows in primary_key_checks:
        values = [row.get(field) for row in rows]

        if any(
            value is None or str(value).strip() == ""
            for value in values
        ):
            errors.append(
                f"Missing or empty primary key: {field}"
            )

        non_empty_values = [
            value for value in values
            if value is not None and str(value).strip() != ""
        ]

        if len(non_empty_values) != len(set(non_empty_values)):
            errors.append(
                f"Duplicate primary key detected: {field}"
            )

    customer_ids = {
        row["customer_id"] for row in customers
    }
    product_ids = {
        row["product_id"] for row in products
    }
    channel_ids = {
        row["channel_id"] for row in channels
    }
    survey_lookup = {
        row["survey_id"]: row for row in surveys
    }
    theme_ids = {
        f"THEME-{index:06d}"
        for index, _ in enumerate(THEMES, start=1)
    }

    # Foreign keys and value constraints for reviews.
    for row in reviews:
        record_id = row.get("review_id", "<unknown>")

        if row.get("customer_id") not in customer_ids:
            errors.append(
                f"Invalid customer foreign key in review {record_id}"
            )

        if row.get("product_id") not in product_ids:
            errors.append(
                f"Invalid product foreign key in review {record_id}"
            )

        if row.get("channel_id") not in channel_ids:
            errors.append(
                f"Invalid channel foreign key in review {record_id}"
            )

        if row.get("theme_id") not in theme_ids:
            errors.append(
                f"Invalid theme foreign key in review {record_id}"
            )

        if row.get("sentiment") not in SENTIMENTS:
            errors.append(
                f"Invalid sentiment in review {record_id}"
            )

        confidence = row.get("sentiment_confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            errors.append(
                f"Invalid sentiment confidence in review {record_id}"
            )

        rating = row.get("rating")
        if not isinstance(rating, int) or not 1 <= rating <= 5:
            errors.append(
                f"Invalid rating in review {record_id}"
            )

        parse_date(
            row.get("created_at"),
            "reviews.created_at",
            errors,
            record_id
        )

    # Foreign keys, date ordering and value constraints for responses.
    for row in responses:
        record_id = row.get("response_id", "<unknown>")

        if row.get("customer_id") not in customer_ids:
            errors.append(
                f"Invalid customer foreign key in response {record_id}"
            )

        if row.get("product_id") not in product_ids:
            errors.append(
                f"Invalid product foreign key in response {record_id}"
            )

        if row.get("channel_id") not in channel_ids:
            errors.append(
                f"Invalid channel foreign key in response {record_id}"
            )

        survey = survey_lookup.get(row.get("survey_id"))
        if survey is None:
            errors.append(
                f"Invalid survey foreign key in response {record_id}"
            )
        else:
            survey_start = parse_date(
                survey.get("start_date"),
                "surveys.start_date",
                errors,
                survey.get("survey_id", "<unknown>")
            )
            submitted_at = parse_date(
                row.get("submitted_at"),
                "survey_responses.submitted_at",
                errors,
                record_id
            )

            if (
                survey_start is not None
                and submitted_at is not None
                and submitted_at < survey_start
            ):
                errors.append(
                    f"Response {record_id} was submitted before "
                    f"survey {survey['survey_id']} started"
                )

        if row.get("theme_id") not in theme_ids:
            errors.append(
                f"Invalid theme foreign key in response {record_id}"
            )

        if row.get("sentiment") not in SENTIMENTS:
            errors.append(
                f"Invalid sentiment in response {record_id}"
            )

        confidence = row.get("sentiment_confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            errors.append(
                f"Invalid sentiment confidence in response {record_id}"
            )

        created_at = parse_date(
            row.get("created_at"),
            "survey_responses.created_at",
            errors,
            record_id
        )
        submitted_at = parse_date(
            row.get("submitted_at"),
            "survey_responses.submitted_at",
            errors,
            record_id
        )

        if (
            created_at is not None
            and submitted_at is not None
            and created_at != submitted_at
        ):
            errors.append(
                f"created_at and submitted_at differ in response {record_id}"
            )

    # Foreign keys and value constraints for support messages.
    for row in messages:
        record_id = row.get("message_id", "<unknown>")

        if row.get("customer_id") not in customer_ids:
            errors.append(
                f"Invalid customer foreign key in message {record_id}"
            )

        if row.get("channel_id") not in channel_ids:
            errors.append(
                f"Invalid channel foreign key in message {record_id}"
            )

        if row.get("theme_id") not in theme_ids:
            errors.append(
                f"Invalid theme foreign key in message {record_id}"
            )

        if row.get("sentiment") not in SENTIMENTS:
            errors.append(
                f"Invalid sentiment in message {record_id}"
            )

        confidence = row.get("sentiment_confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            errors.append(
                f"Invalid sentiment confidence in message {record_id}"
            )

        parse_date(
            row.get("created_at"),
            "support_messages.created_at",
            errors,
            record_id
        )

    # Intentionally do NOT validate predicted_theme against the taxonomy
    # here. The injected "Billing" value is an expected audit anomaly.
    # Likewise, the duplicate business submission is intentionally retained
    # for the anomaly scanner; its primary key remains unique.

    return errors


# =========================================================
# 10. MAIN GENERATOR
# =========================================================

def main():
    global GENERATED_DIR, GROUND_TRUTH_DIR, MANIFEST_DIR
    
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

    # Keep starter and full-scale datasets in separate directories.
    if args.scale == "full":
        GENERATED_DIR = BASE_DIR / "data" / "generated_full"
        GROUND_TRUTH_DIR = BASE_DIR / "data" / "ground_truth_full"
        MANIFEST_DIR = BASE_DIR / "data" / "manifests_full"
    else:
        GENERATED_DIR = BASE_DIR / "data" / "generated"
        GROUND_TRUTH_DIR = BASE_DIR / "data" / "ground_truth"
        MANIFEST_DIR = BASE_DIR / "data" / "manifests"

    rng = random.Random(args.seed)

    # Dataset sizes.
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

    # Create output directories.
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating InsightPulse AI synthetic data...")
    print(f"Scale: {args.scale}")
    print(f"Seed: {args.seed}")

    # Generate master tables first.
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

    # Generate feedback tables.
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

    # Inject known edge cases after baseline generation.
    ground_truth, leakage_probe = inject_edge_cases(
        reviews,
        responses,
        messages
    )

    # Generate derived action items from the feedback records.
    action_items = generate_action_items(
        reviews,
        responses,
        messages
    )

    # Export master tables.
    write_csv("customers.csv", customers)
    write_csv("products.csv", products)
    write_csv("channels.csv", channels)
    write_csv("surveys.csv", surveys)
    write_csv("themes.csv", themes)
    write_csv("sentiment_labels.csv", sentiment_labels)

    # Export event tables.
    write_csv("reviews.csv", reviews)
    write_csv("survey_responses.csv", responses)
    write_csv("support_messages.csv", messages)
    write_csv("action_items.csv", action_items)

    # Deliberately contaminated fixture. Never use as production model input.
    write_csv(
        "model_input_adversarial.csv",
        leakage_probe
    )

    # Keep evaluation ground truth separate from model inputs.
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

    # Validate generated data.
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

    # Validation summary.
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

    # Source manifest and file checksums.
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

    print("\nGeneration completed.")
    print(json.dumps(summary, indent=2))

    if validation_errors:
        raise SystemExit(
            "Dataset validation failed. Check the errors above."
        )

    print(
        "\nSynthetic data generation and baseline validation passed."
    )


if __name__ == "__main__":
    main()
