
# InsightPulse AI — Data Dictionary

## 1. Project Overview

InsightPulse AI is a customer feedback intelligence platform that combines reviews, survey responses and support messages to identify recurring themes, sentiment shifts, service priorities and data anomalies.

### Synthetic Data Configuration

- Random seed: `20261022`
- Reviews and survey responses combined: 50,000
- Support messages: 20,000
- Sentiment labels: Positive, Negative, Neutral, Mixed
- Theme labels: Performance, Customer Support, Feature Request
- Ground truth: Stored separately and never provided to prediction models.

## 2. ID Conventions

| Entity | ID format | Example |
|---|---|---|
| Customer | CUS-000001 | CUS-000001 |
| Product | PROD-000001 | PROD-000001 |
| Channel | CH-001 | CH-001 |
| Survey | SUR-2026-000001 | SUR-2026-000001 |
| Survey Response | RESP-SUR-2026-000001-001 | RESP-SUR-2026-000001-001 |
| Review | REV-2026-000001 | REV-2026-000001 |
| Support Message | MSG-TKT-000001-001 | MSG-TKT-000001-001 |
| Theme | THEME-000001 | THEME-000001 |
| Sentiment | SENT-001 | SENT-001 |
| Action Item | ACT-2026-000001 | ACT-2026-000001 |

All IDs are immutable, unique and generated deterministically.

## 3. Core Entities

### 3.1 Customer

| Field | Type | Required | Validation |
|---|---|---|---|
| customer_id | String | Yes | Unique CUS identifier |
| customer_name | String | Yes | Synthetic name |
| email | String | No | Valid synthetic email; no real personal data |
| country | String | Yes | Supported country name |
| created_at | Datetime | Yes | Valid timestamp |

### 3.2 Product

| Field | Type | Required | Validation |
|---|---|---|---|
| product_id | String | Yes | Unique PROD identifier |
| product_name | String | Yes | Non-empty |
| category | String | Yes | Approved product category |
| description | String | No | Synthetic description |
| created_at | Datetime | Yes | Valid timestamp |

### 3.3 Channel

| Field | Type | Required | Validation |
|---|---|---|---|
| channel_id | String | Yes | Unique CH identifier |
| channel_name | String | Yes | Web, iOS, Email, In-App |
| description | String | No | Channel description |
| created_at | Datetime | Yes | Valid timestamp |

### 3.4 Survey

| Field | Type | Required | Validation |
|---|---|---|---|
| survey_id | String | Yes | SUR-2026 identifier |
| survey_title | String | Yes | Non-empty |
| description | String | No | Survey description |
| status | String | Yes | draft, active, closed |
| created_at | Datetime | Yes | Valid timestamp |

### 3.5 SurveyResponse

| Field | Type | Required | Validation |
|---|---|---|---|
| response_id | String | Yes | Unique RESP identifier |
| survey_id | String | Yes | Valid Survey foreign key |
| customer_id | String | Yes | Valid Customer foreign key |
| product_id | String | Yes | Valid Product foreign key |
| channel_id | String | Yes | Valid Channel foreign key |
| response_text | String | Yes | Non-empty synthetic feedback |
| rating | Integer | No | 1–5 |
| sentiment | String | Yes | Positive, Negative, Neutral, Mixed |
| theme | String | Yes | Approved theme taxonomy |
| submitted_at | Datetime | Yes | Within survey effective dates |

### 3.6 Review

| Field | Type | Required | Validation |
|---|---|---|---|
| review_id | String | Yes | REV-2026 identifier |
| customer_id | String | Yes | Valid Customer foreign key |
| product_id | String | Yes | Valid Product foreign key |
| channel_id | String | Yes | Valid Channel foreign key |
| review_text | String | Yes | Non-empty synthetic feedback |
| rating | Integer | No | 1–5 |
| sentiment | String | Yes | Four approved sentiment labels |
| sentiment_confidence | Float | No | 0.0–1.0 |
| theme_id | String | No | Valid Theme foreign key |
| created_at | Datetime | Yes | Valid event timestamp |

### 3.7 SupportMessage

| Field | Type | Required | Validation |
|---|---|---|---|
| message_id | String | Yes | MSG ticket identifier |
| customer_id | String | Yes | Valid Customer foreign key |
| channel_id | String | Yes | Valid Channel foreign key |
| ticket_id | String | Yes | Valid synthetic ticket identifier |
| message_text | String | Yes | Non-empty synthetic support text |
| sentiment | String | Yes | Four approved sentiment labels |
| sentiment_confidence | Float | No | 0.0–1.0 |
| theme_id | String | No | Valid Theme foreign key |
| created_at | Datetime | Yes | Valid event timestamp |

### 3.8 Theme

| Field | Type | Required | Validation |
|---|---|---|---|
| theme_id | String | Yes | THEME-000001 format |
| theme_name | String | Yes | Approved taxonomy value |
| description | String | No | Theme description |

Allowed theme values:

- Performance
- Customer Support
- Feature Request

### 3.9 SentimentLabel

| Field | Type | Required | Validation |
|---|---|---|---|
| sentiment_id | String | Yes | Unique SENT identifier |
| sentiment_name | String | Yes | Approved sentiment |
| description | String | No | Sentiment definition |

Allowed sentiment values:

- Positive
- Negative
- Neutral
- Mixed

### 3.10 ActionItem

| Field | Type | Required | Validation |
|---|---|---|---|
| action_id | String | Yes | ACT-2026 identifier |
| theme_id | String | Yes | Valid Theme foreign key |
| action_title | String | Yes | Non-empty |
| description | String | Yes | Action explanation |
| priority | String | Yes | low, medium, high, critical |
| status | String | Yes | open, in_progress, resolved |
| created_at | Datetime | Yes | Valid timestamp |

## 4. Supporting Entities

The following supporting tables preserve traceability and audit history.

### 4.1 ActionItemFeedback

Purpose: Links ActionItems to the exact reviews, survey responses and support messages that triggered them.

- action_id: Foreign key to ActionItem.
- source_type: review, survey_response or support_message.
- source_id: Exact source record identifier.

Relationship: Many-to-many between ActionItem and feedback records.

### 4.2 ActionItemHistory

Purpose: Preserves every ActionItem status change instead of overwriting history.

- history_id: Unique identifier.
- action_id: Foreign key to ActionItem.
- previous_status: Previous lifecycle state.
- new_status: New lifecycle state.
- changed_at: Timestamp.
- changed_by: System or synthetic user identifier.
- reason: Explanation of change.

### 4.3 AnomalyRecord

Purpose: Stores detected data quality and exception issues.

- anomaly_id: Unique identifier.
- source_type: review, survey_response or support_message.
- source_id: Exact source record identifier.
- issue_type: Anomaly category.
- severity: low, medium, high or critical.
- description: Explanation.
- status: open, reviewed or resolved.
- detected_at: Timestamp.

## 5. Relationships and Cardinality

| Parent | Child | Relationship |
|---|---|---|
| Customer | Review | One-to-many |
| Customer | SurveyResponse | One-to-many |
| Customer | SupportMessage | One-to-many |
| Product | Review | One-to-many |
| Product | SurveyResponse | One-to-many |
| Channel | Review | One-to-many |
| Channel | SurveyResponse | One-to-many |
| Channel | SupportMessage | One-to-many |
| Survey | SurveyResponse | One-to-many |
| Theme | Review | One-to-many, optional |
| Theme | SurveyResponse | One-to-many |
| Theme | SupportMessage | One-to-many |
| Theme | ActionItem | One-to-many |
| ActionItem | ActionItemFeedback | One-to-many |
| ActionItem | ActionItemHistory | One-to-many |

ActionItem and feedback records have a many-to-many relationship through ActionItemFeedback.

## 6. Sentiment and Theme Business Rules

1. Every analysed feedback record receives one of four sentiment labels.
2. Every analysed feedback record receives one of three approved theme labels.
3. Mixed sentiment represents feedback containing both positive and negative signals.
4. The model must not receive ground-truth labels as input.
5. Predictions and ground-truth labels must be stored separately.
6. Confidence scores must be between 0 and 1.
7. Invalid theme assignments must be detected and recorded as anomalies.

## 7. Data Generation Rules

1. Generate master records before dependent records.
2. Generate valid foreign-key relationships.
3. Use a fixed random seed of 20261022.
4. Generate 50,000 reviews and survey responses combined.
5. Generate 20,000 support messages.
6. Include multilingual, neutral, mixed, sarcastic and ambiguous examples.
7. Generate valid baseline records before injecting anomalies.
8. Generate ground truth separately from model inputs.
9. Derive totals, scores and statuses from source records.
10. Validate primary keys, foreign keys, allowed values and dates.

## 8. Required Anomaly Types

| Issue type | Expected detection |
|---|---|
| Contradictory label | Compare assigned sentiment with feedback text |
| Duplicate response | Identify repeated survey submissions |
| PII leakage | Detect email addresses and other personal identifiers |
| Invalid theme | Detect themes outside the approved taxonomy |
| Ground-truth leakage | Ensure evaluation labels are excluded from model inputs |

## 9. Evaluation

Predictions will be compared with separately maintained ground-truth labels.

Metrics:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

Evaluation will be performed separately for sentiment and theme classification.

## 10. Reproducibility

The generator must:

- Accept a configurable seed.
- Support starter and full dataset sizes.
- Produce deterministic IDs.
- Generate repeatable records with the same seed.
- Export CSV and JSON files.
- Produce validation and checksum reports.
