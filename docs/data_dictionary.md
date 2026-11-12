# InsightPulse AI — Data Dictionary

## 1. Project Overview

InsightPulse AI is a Customer Feedback Intelligence Platform that combines customer reviews, survey responses, and support messages to identify recurring themes, sentiment patterns, service priorities, and data-quality anomalies.

### Synthetic Data Configuration

| Configuration | Value |
|---|---|
| Random seed | `20261022` |
| Reviews | 30,000 |
| Survey responses | 20,001 |
| Support messages | 20,000 |
| Total feedback records | 70,001 |
| Sentiment categories | Positive, Negative, Neutral, Mixed |
| Theme categories | Performance, Customer Support, Feature Request |
| Data provenance | Synthetic data |
| Ground truth | Stored separately from model-training inputs |

The generator supports starter and full dataset configurations.

## 2. ID Conventions

| Entity | ID format | Example |
|---|---|---|
| Customer | CUS-000001 | CUS-000001 |
| Product | PROD-000001 | PROD-000001 |
| Channel | CH-001 | CH-001 |
| Survey | SUR-2026-000001 | SUR-2026-000001 |
| Survey Response | RESP-SUR-2026-000001-001 | RESP-SUR-2026-000001-001 |
| Review | REV-2026-000001 | REV-2026-000001 |
| Support Message | MSG-TKT-2026-000001-001 | MSG-TKT-2026-000001-001 |
| Theme | THEME-000001 | THEME-000001 |
| Sentiment | SENT-001 | SENT-001 |
| Action Item | ACT-000001 or generated identifier | ACT-000001 |
| Anomaly | Generated anomaly identifier | ANOM-... |

Generated identifiers are used to identify records and maintain relationships. The generator uses a fixed random seed by default. Automatically generated action-item identifiers may use UUID-based values.

Primary keys are immutable record identifiers within the application.

## 3. Core Entities

The following sections describe the ten core entities and their implemented database fields.

**Field notation:**
- Required: database column is declared NOT NULL.
- Optional: database column permits NULL.
- Default: value supplied by the database when one is configured.
- Primary key: identifies a unique database record.

### 3.1 Customer

**Table:** `customers`

**Purpose:** Stores synthetic customer information.

| Field | SQL type | Required | Key / Default | Description and validation |
|---|---|---|---|---|
| customer_id | VARCHAR(50) | Yes | Primary key | Customer identifier |
| customer_name | VARCHAR(150) | Yes | — | Synthetic customer name |
| email | VARCHAR(150) | No | — | Synthetic email address |
| country | VARCHAR(100) | No | — | Customer country |
| created_at | DATETIME | No | CURRENT_TIMESTAMP | Record creation timestamp |

### 3.2 Product

**Table:** `products`

**Purpose:** Stores product information associated with customer feedback.

| Field | SQL type | Required | Key / Default | Description and validation |
|---|---|---|---|---|
| product_id | VARCHAR(50) | Yes | Primary key | Product identifier |
| product_name | VARCHAR(150) | Yes | — | Non-empty product name |
| category | VARCHAR(100) | Yes | — | Product category |
| description | TEXT | No | — | Product description |
| created_at | DATETIME | No | CURRENT_TIMESTAMP | Record creation timestamp |

### 3.3 Channel

**Table:** `channels`

**Purpose:** Identifies the channel through which customer feedback is received.

| Field | SQL type | Required | Key / Default | Description and validation |
|---|---|---|---|---|
| channel_id | VARCHAR(50) | Yes | Primary key | Channel identifier |
| channel_name | VARCHAR(100) | Yes | — | Channel name |
| description | VARCHAR(250) | No | — | Channel description |
| created_at | DATETIME | No | CURRENT_TIMESTAMP | Record creation timestamp |

### 3.4 Survey

**Table:** `surveys`

**Purpose:** Stores survey information used to collect customer responses.

| Field | SQL type | Required | Key / Default | Description and validation |
|---|---|---|---|---|
| survey_id | VARCHAR(50) | Yes | Primary key | Survey identifier |
| survey_title | VARCHAR(200) | Yes | — | Survey title |
| description | TEXT | No | — | Survey description |
| status | VARCHAR(30) | Yes | — | Survey lifecycle status |
| created_at | DATETIME | No | CURRENT_TIMESTAMP | Record creation timestamp |

### 3.5 SurveyResponse

**Table:** `survey_responses`

**Purpose:** Stores customer responses submitted through surveys.

| Field | SQL type | Required | Key / Default | Description and validation |
|---|---|---|---|---|
| response_id | VARCHAR(100) | Yes | Primary key | Survey response identifier |
| survey_id | VARCHAR(50) | Yes | FK → surveys.survey_id | Associated survey |
| customer_id | VARCHAR(50) | Yes | FK → customers.customer_id | Responding customer |
| product_id | VARCHAR(50) | Yes | FK → products.product_id | Associated product |
| channel_id | VARCHAR(50) | Yes | FK → channels.channel_id | Feedback channel |
| response_text | TEXT | Yes | — | Synthetic survey feedback |
| sentiment | VARCHAR(20) | No | — | Sentiment value when available |
| sentiment_confidence | FLOAT | No | — | Prediction confidence, when available |
| theme_id | VARCHAR(50) | No | FK → themes.theme_id | Optional associated theme |
| predicted_theme | VARCHAR(100) | No | — | Predicted theme value |
| submitted_at | DATETIME | Yes | CURRENT_TIMESTAMP | Submission timestamp |

**Important schema note:** The implemented `survey_responses` table does not contain a `rating` column.

### 3.6 Review

**Table:** `reviews`

**Purpose:** Stores customer product reviews and their associated analysis results.

| Field | SQL type | Required | Key / Default | Description and validation |
|---|---|---|---|---|
| review_id | VARCHAR(50) | Yes | Primary key | Review identifier |
| customer_id | VARCHAR(50) | Yes | FK → customers.customer_id | Reviewing customer |
| product_id | VARCHAR(50) | Yes | FK → products.product_id | Reviewed product |
| channel_id | VARCHAR(50) | Yes | FK → channels.channel_id | Feedback channel |
| review_text | TEXT | Yes | — | Synthetic review text |
| rating | INTEGER | No | — | Review rating, where supplied |
| sentiment | VARCHAR(20) | No | — | Sentiment value when available |
| sentiment_confidence | FLOAT | No | — | Prediction confidence, when available |
| theme_id | VARCHAR(50) | No | FK → themes.theme_id | Optional associated theme |
| predicted_theme | VARCHAR(100) | No | — | Predicted theme value |
| created_at | DATETIME | Yes | CURRENT_TIMESTAMP | Review creation timestamp |

### 3.7 SupportMessage

**Table:** `support_messages`

**Purpose:** Stores customer support conversations and feedback.

| Field | SQL type | Required | Key / Default | Description and validation |
|---|---|---|---|---|
| message_id | VARCHAR(100) | Yes | Primary key | Support message identifier |
| customer_id | VARCHAR(50) | Yes | FK → customers.customer_id | Associated customer |
| channel_id | VARCHAR(50) | Yes | FK → channels.channel_id | Feedback channel |
| ticket_id | VARCHAR(50) | Yes | — | Associated ticket identifier |
| message_text | TEXT | Yes | — | Synthetic support message |
| sentiment | VARCHAR(20) | No | — | Sentiment value when available |
| sentiment_confidence | FLOAT | No | — | Prediction confidence, when available |
| theme_id | VARCHAR(50) | No | FK → themes.theme_id | Optional associated theme |
| predicted_theme | VARCHAR(100) | No | — | Predicted theme value |
| created_at | DATETIME | Yes | CURRENT_TIMESTAMP | Message creation timestamp |

### 3.8 Theme

**Table:** `themes`

**Purpose:** Defines customer feedback classification categories.

| Field | SQL type | Required | Key / Default | Description and validation |
|---|---|---|---|---|
| theme_id | VARCHAR(50) | Yes | Primary key | Theme identifier |
| theme_name | VARCHAR(100) | Yes | — | Theme name |
| description | TEXT | No | — | Theme description |
| created_at | DATETIME | Yes | CURRENT_TIMESTAMP | Record creation timestamp |

Configured theme categories:

- Performance
- Customer Support
- Feature Request

### 3.9 SentimentLabel

**Table:** `sentiment_labels`

**Purpose:** Defines the sentiment categories used by the feedback analysis system.

| Field | SQL type | Required | Key / Default | Description and validation |
|---|---|---|---|---|
| sentiment_id | VARCHAR(50) | Yes | Primary key | Sentiment identifier |
| sentiment_name | VARCHAR(50) | Yes | — | Sentiment category |
| description | TEXT | No | — | Sentiment definition |
| created_at | DATETIME | Yes | CURRENT_TIMESTAMP | Record creation timestamp |

Configured sentiment categories:

- Positive
- Negative
- Neutral
- Mixed

**Important schema note:** This is a standalone lookup table. The sentiment fields in reviews, survey responses, and support messages do not have enforced foreign keys to `sentiment_labels`.

### 3.10 ActionItem

**Table:** `action_items`

**Purpose:** Stores recommended actions generated from customer feedback analysis.

| Field | SQL type | Required | Key / Default | Description and validation |
|---|---|---|---|---|
| action_id | VARCHAR(50) | Yes | Primary key | Action identifier |
| theme_id | VARCHAR(50) | Yes | FK → themes.theme_id | Associated feedback theme |
| action_title | VARCHAR(200) | Yes | — | Action title |
| description | TEXT | Yes | — | Action explanation |
| priority | VARCHAR(30) | Yes | — | Configured priority |
| status | VARCHAR(30) | Yes | — | Action status |
| source_count | INTEGER | Yes | — | Number of linked feedback records |
| negative_percentage | FLOAT | No | — | Percentage of negative feedback |
| threshold_percentage | FLOAT | No | — | Configured trigger threshold |
| created_at | DATETIME | Yes | CURRENT_TIMESTAMP | Action creation timestamp |

The configured automatic action-generation threshold is 15%.

Priority and recommendation rules are applied by the application. The database column types alone do not enforce the permitted priority or status values.

## 4. Supporting Entities

The following supporting entities provide source traceability and data-quality information.

### 4.1 ActionItemFeedback

**Table:** `action_item_feedback`

**Purpose:** Links action items to the feedback records used as supporting evidence.

| Field | SQL type | Required | Key / Default | Description and validation |
|---|---|---|---|---|
| mapping_id | VARCHAR(50) | Yes | Primary key | Mapping identifier |
| action_id | VARCHAR(50) | Yes | FK → action_items.action_id | Associated action |
| source_type | VARCHAR(30) | Yes | — | Review, SurveyResponse or SupportMessage |
| source_id | VARCHAR(100) | Yes | Logical reference | Identifier of the source feedback record |
| created_at | DATETIME | Yes | CURRENT_TIMESTAMP | Mapping creation timestamp |

**Relationship:** ActionItem and feedback records have a many-to-many relationship through ActionItemFeedback.

**Reference integrity:** `action_id` is enforced as a database foreign key. `source_id` is a logical reference because it can identify records in different feedback tables. The application resolves the source using `source_type` and `source_id`.

### 4.2 ActionItemHistory — Planned

**Purpose:** Proposed functionality for preserving action-item status changes as separate history records.

This entity is not currently implemented in the database.

Proposed fields:

- history_id: Unique history identifier.
- action_id: Foreign key to ActionItem.
- previous_status: Previous lifecycle state.
- new_status: Updated lifecycle state.
- changed_at: Timestamp of the change.
- changed_by: System or user identifier.
- reason: Explanation for the change.

Historical lifecycle tracking must be treated as planned functionality until an implementation is added and verified.

### 4.3 AnomalyRecord

**Table:** `anomaly_records`

**Purpose:** Stores detected data-quality and exception issues.

| Field | SQL type | Required | Key / Default | Description and validation |
|---|---|---|---|---|
| anomaly_id | VARCHAR(50) | Yes | Primary key | Anomaly identifier |
| source_type | VARCHAR(50) | Yes | — | Source feedback type |
| source_id | VARCHAR(100) | Yes | Logical reference | Affected source record identifier |
| anomaly_type | VARCHAR(100) | Yes | — | Anomaly category |
| severity | VARCHAR(20) | Yes | — | Anomaly severity |
| description | TEXT | Yes | — | Explanation of the anomaly |
| details | TEXT | No | — | Additional anomaly information |
| status | VARCHAR(30) | Yes | — | Anomaly review status |
| detected_at | DATETIME | Yes | — | Detection timestamp |

**Reference integrity:** The anomaly table has no database-enforced foreign keys. Its `source_type` and `source_id` fields are used as logical references to the affected source records.

**Important schema note:** The `details` column is stored as TEXT in SQLite, not as a native JSON column.

### 4.4 Source Traceability and Privacy

**Source retrieval:** The ActionItem source API retrieves linked feedback using `action_id`, `source_type`, and `source_id`.

The source response includes the source type, source identifier, feedback text, sentiment, and timestamp.

**PII protection in supported source API responses:**

- Email addresses are replaced with `[REDACTED EMAIL]`.
- Indian phone numbers are replaced with `[REDACTED PHONE]`.
- Original feedback text remains unchanged in the database.
- Original records are retained for anomaly detection and investigation.

The masking behavior applies to supported API response workflows; it should not be interpreted as encryption or removal of original source data.

## 5. Relationships and Cardinality

The following relationships reflect the implemented database foreign keys.

| Parent | Child | Cardinality | Optionality |
|---|---|---|---|
| Customer | Review | 1:N | Review requires customer |
| Customer | SurveyResponse | 1:N | Response requires customer |
| Customer | SupportMessage | 1:N | Message requires customer |
| Product | Review | 1:N | Review requires product |
| Product | SurveyResponse | 1:N | Response requires product |
| Channel | Review | 1:N | Review requires channel |
| Channel | SurveyResponse | 1:N | Response requires channel |
| Channel | SupportMessage | 1:N | Message requires channel |
| Survey | SurveyResponse | 1:N | Response requires survey |
| Theme | Review | 1:N | Review theme is optional |
| Theme | SurveyResponse | 1:N | Response theme is optional |
| Theme | SupportMessage | 1:N | Message theme is optional |
| Theme | ActionItem | 1:N | Action requires theme |
| ActionItem | ActionItemFeedback | 1:N | Mapping requires action |

ActionItem and feedback records have a many-to-many relationship through ActionItemFeedback.

The `source_id` field in ActionItemFeedback is a logical reference, not a database-enforced foreign key.

AnomalyRecord also uses logical source references and does not enforce foreign keys to the feedback tables.

SentimentLabel is a standalone lookup table and does not have enforced relationships to the feedback sentiment fields.

### Database integrity notes

- Primary keys are defined for all 12 implemented tables.
- The foreign-key relationships listed above are enforced by the schema.
- Optional relationships are represented by nullable foreign-key columns.
- No additional uniqueness constraints on fields such as customer email, product name, channel name, or theme name are established by the inspected schema.
- Application-level validation and database-level constraints should be distinguished when documenting allowed values.

## 6. Sentiment and Theme Business Rules

1. The platform uses four sentiment categories: Positive, Negative, Neutral, and Mixed.
2. The configured theme taxonomy contains Performance, Customer Support, and Feature Request.
3. Mixed sentiment represents feedback containing both positive and negative signals.
4. Model predictions and ground-truth evaluation labels must remain separate.
5. Ground-truth labels must not be used as prediction input.
6. Prediction confidence values are represented as floating-point values.
7. Invalid theme assignments are identified as data-quality issues.
8. Original feedback records are retained.
9. PII is masked in supported source API responses.
10. Action-item recommendations are associated with supporting feedback records.

## 7. Data Generation Rules

The synthetic data generator uses the following documented configuration and rules:

1. Generate master records before dependent records.
2. Generate dependent records using valid parent identifiers.
3. Use a fixed random seed of `20261022` by default.
4. Generate 30,000 reviews and 20,001 survey responses in the full dataset.
5. Generate 20,000 support messages in the full dataset.
6. Include multilingual, neutral, mixed, sarcastic, and ambiguous examples.
7. Generate baseline records before injecting deliberate anomaly cases.
8. Keep ground-truth data separate from model inputs.
9. Derive analytical totals and percentages from source records.
10. Validate primary keys, foreign keys, allowed values, dates, and duplicate cases.
11. Preserve the distinction between source feedback, model predictions, and ground-truth labels.
12. Export generated data and validation information in the supported formats.

### Dataset counts

| Dataset | Full-scale records |
|---|---:|
| Customers | 5,000 |
| Products | 5 |
| Channels | 5 |
| Surveys | 100 |
| Reviews | 30,000 |
| Survey Responses | 20,001 |
| Support Messages | 20,000 |
| Total feedback records | 70,001 |

The full dataset includes one deliberately injected duplicate survey response.

### Sentiment distribution

| Sentiment | Records |
|---|---:|
| Positive | 17,501 |
| Neutral | 17,500 |
| Negative | 17,500 |
| Mixed | 17,500 |

## 8. Required Anomaly Types

| Issue type | Expected detection |
|---|---|
| Contradictory sentiment label | Detect disagreement between the stored label and feedback text |
| Duplicate response | Identify repeated survey submissions |
| PII leakage | Detect synthetic email addresses and other personal identifiers |
| Invalid theme | Detect themes outside the approved taxonomy |
| Ground-truth leakage | Prevent evaluation labels from entering model-training inputs |
| Rating-text mismatch | Identify inconsistencies between review ratings and feedback text |

Detected anomalies are stored in AnomalyRecord and made available through the anomaly management functionality.

Ground-truth records are reserved for evaluation and must never be used as prediction input.

## 9. Model Preparation and Evaluation

### Sentiment model preparation

The sentiment training pipeline uses:

1. Synthetic review text.
2. Text preprocessing.
3. Duplicate and conflicting-label removal.
4. Ground-truth review exclusion.
5. TF-IDF vectorization using unigrams and bigrams.
6. Logistic Regression classification.
7. Stratified training and testing split.

The dataset preparation script excludes review records identified in the separate ground-truth dataset.

The training process also rejects evaluation-related columns such as:

- `test_label`
- `ground_truth`
- `expected_sentiment`
- `expected_decision`
- `issue_type`

### Latest recorded sentiment evaluation

| Metric | Result |
|---|---:|
| Test accuracy | 68.97% |
| Training examples | 115 |
| Testing examples | 29 |
| Total prepared examples | 144 |
| Sentiment classes | 4 |

The prepared dataset contains 36 unique examples per sentiment category.

These results are preliminary and are based on a small synthetic training dataset. They should not be interpreted as production-level accuracy or proven generalization to real customer feedback.

### Evaluation metrics

The evaluation framework identifies the following metrics:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

Theme classification evaluation should be reported separately when measured results are available. No theme evaluation score is asserted in this document.

## 10. Ground-Truth Isolation

The ground-truth dataset is maintained separately from model-training inputs.

The six documented evaluation cases cover:

1. Sentiment-label contradiction.
2. Duplicate survey submission.
3. PII leakage.
4. Invalid theme assignment.
5. Rating-text mismatch.
6. Model-input leakage.

The preparation process identifies three ground-truth review records and excludes them from the sentiment training dataset.

The latest recorded preparation result:

| Check | Result |
|---|---:|
| Original input rows | 30,000 |
| Ground-truth review records identified | 3 |
| Ground-truth review records excluded | 3 |
| Conflicting text examples removed | 9 |
| Duplicate sentences removed | 29,281 |
| Final prepared unique examples | 144 |
| Ground-truth leakage check | PASSED |

## 11. Reproducibility and Validation

The synthetic data generator supports a configurable random seed and starter/full dataset configurations.

The project generates validation manifests containing dataset information, row counts, checksums, and validation results.

### Verified validation results

- Full dataset manifest validation passed.
- No validation errors were reported in the recorded full dataset validation.
- Six ground-truth evaluation cases were verified.
- The deliberately injected duplicate survey response was verified.
- Ground-truth review exclusion from sentiment training was verified.
- The prepared sentiment dataset passed its ground-truth leakage check.

### Reproducibility status

The fixed seed and checksum manifests support reproducible dataset generation.

A separate two-run comparison using identical configuration and seed should be retained as evidence before claiming that independent regeneration has been fully verified.

## 12. Implemented Database Tables

The inspected SQLite database contains 12 implemented tables:

| Table | Purpose |
|---|---|
| customers | Customer information |
| products | Product information |
| channels | Feedback channel information |
| surveys | Survey information |
| survey_responses | Customer survey feedback |
| reviews | Customer product reviews |
| support_messages | Support conversations |
| themes | Feedback theme definitions |
| sentiment_labels | Sentiment category definitions |
| action_items | Generated recommendations |
| action_item_feedback | Action-to-source-feedback mappings |
| anomaly_records | Detected data-quality anomalies |

ActionItemHistory is a planned entity and is not included in the implemented database.

## 13. Data Dictionary Scope and Limitations

This document describes the inspected SQLite schema and the documented application behavior.

The following distinctions are important:

- Database-enforced foreign keys are documented separately from logical source references.
- Optional fields are based on the actual SQLite nullability metadata.
- Database column types are documented as inspected.
- Application-level validation rules are not automatically database constraints.
- Planned history tracking is not described as implemented functionality.
- Evaluation metrics are only reported where recorded results are available.
- Reproducibility claims must be supported by repeat-generation evidence.

---

**Project:** InsightPulse AI — Customer Feedback Intelligence Platform

**Repository:** https://github.com/nikhithabhandary08/insightpulse-ai