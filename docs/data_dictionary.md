# InsightPulse AI — Data Dictionary

## 1. Project Overview

InsightPulse AI is a Customer Feedback Intelligence Platform that combines product reviews, survey responses and support messages to identify recurring themes, sentiment shifts, service priorities and data quality anomalies.

### Synthetic Data Configuration

- Random seed: `20261022`
- Reviews and survey responses combined: 50,001 (full scale, including one intentionally injected duplicate survey response)
- Support messages: 20,000 (full scale)
- Sentiment labels: Positive, Negative, Neutral, Mixed
- Theme labels: Performance, Customer Support, Feature Request
- Ground truth: Stored separately and never provided to prediction models.
- Dataset generation: Synthetic data only.

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
| Action Item | ACT-000001 or ACT-AUTO-... | ACT-000001 |
| Anomaly | ANOM-... | Generated anomaly identifier |

IDs are used to identify records and maintain relationships between entities. Generated records use a fixed random seed. Automatically generated ActionItem identifiers may use UUID-based values.

## 3. Core Entities

### 3.1 Customer

**Purpose:** Stores synthetic customer information.

| Field | Type | Required | Validation |
|---|---|---|---|
| customer_id | String | Yes | Unique customer identifier |
| customer_name | String | Yes | Synthetic customer name |
| email | String | No | Synthetic email address |
| country | String | Yes | Supported country name |
| created_at | Datetime | Yes | Valid timestamp |

### 3.2 Product

**Purpose:** Stores product information associated with customer feedback.

| Field | Type | Required | Validation |
|---|---|---|---|
| product_id | String | Yes | Unique product identifier |
| product_name | String | Yes | Non-empty |
| category | String | Yes | Approved product category |
| description | String | No | Synthetic description |
| created_at | Datetime | Yes | Valid timestamp |

### 3.3 Channel

**Purpose:** Identifies the channel through which customer feedback is received.

| Field | Type | Required | Validation |
|---|---|---|---|
| channel_id | String | Yes | Unique channel identifier |
| channel_name | String | Yes | Supported channel name |
| description | String | No | Channel description |
| created_at | Datetime | Yes | Valid timestamp |

### 3.4 Survey

**Purpose:** Stores survey information used to collect customer responses.

| Field | Type | Required | Validation |
|---|---|---|---|
| survey_id | String | Yes | Unique survey identifier |
| survey_title | String | Yes | Non-empty |
| description | String | No | Survey description |
| status | String | Yes | Draft, Active or Closed |
| created_at | Datetime | Yes | Valid timestamp |

### 3.5 SurveyResponse

**Purpose:** Stores customer responses submitted through surveys.

| Field | Type | Required | Validation |
|---|---|---|---|
| response_id | String | Yes | Unique response identifier |
| survey_id | String | Yes | Valid Survey foreign key |
| customer_id | String | Yes | Valid Customer foreign key |
| product_id | String | Yes | Valid Product foreign key |
| channel_id | String | Yes | Valid Channel foreign key |
| response_text | String | Yes | Non-empty synthetic feedback |
| rating | Integer | No | Value between 1 and 5 |
| sentiment | String | Yes | Positive, Negative, Neutral or Mixed |
| theme | String | Yes | Approved theme taxonomy |
| submitted_at | Datetime | Yes | Valid submission timestamp |

### 3.6 Review

**Purpose:** Stores customer product reviews and their associated analysis results.

| Field | Type | Required | Validation |
|---|---|---|---|
| review_id | String | Yes | Unique review identifier |
| customer_id | String | Yes | Valid Customer foreign key |
| product_id | String | Yes | Valid Product foreign key |
| channel_id | String | Yes | Valid Channel foreign key |
| review_text | String | Yes | Non-empty synthetic feedback |
| rating | Integer | No | Value between 1 and 5 |
| sentiment | String | Yes | Positive, Negative, Neutral or Mixed |
| sentiment_confidence | Float | No | Value between 0.0 and 1.0 |
| theme_id | String | No | Valid Theme foreign key |
| created_at | Datetime | Yes | Valid event timestamp |

### 3.7 SupportMessage

**Purpose:** Stores customer support conversations and feedback.

| Field | Type | Required | Validation |
|---|---|---|---|
| message_id | String | Yes | Unique support message identifier |
| customer_id | String | Yes | Valid Customer foreign key |
| channel_id | String | Yes | Valid Channel foreign key |
| ticket_id | String | Yes | Valid synthetic ticket identifier |
| message_text | String | Yes | Non-empty synthetic support text |
| sentiment | String | Yes | Positive, Negative, Neutral or Mixed |
| sentiment_confidence | Float | No | Value between 0.0 and 1.0 |
| theme_id | String | No | Valid Theme foreign key |
| created_at | Datetime | Yes | Valid event timestamp |

### 3.8 Theme

**Purpose:** Defines the approved customer feedback classification categories.

| Field | Type | Required | Validation |
|---|---|---|---|
| theme_id | String | Yes | Unique theme identifier |
| theme_name | String | Yes | Approved taxonomy value |
| description | String | No | Theme description |

Allowed theme values:

- Performance
- Customer Support
- Feature Request

### 3.9 SentimentLabel

**Purpose:** Defines the sentiment categories used for feedback analysis.

| Field | Type | Required | Validation |
|---|---|---|---|
| sentiment_id | String | Yes | Unique sentiment identifier |
| sentiment_name | String | Yes | Approved sentiment value |
| description | String | No | Sentiment definition |

Allowed sentiment values:

- Positive
- Negative
- Neutral
- Mixed

### 3.10 ActionItem

**Purpose:** Stores recommended actions generated from customer feedback analysis.

| Field | Type | Required | Validation |
|---|---|---|---|
| action_id | String | Yes | Unique action identifier |
| theme_id | String | Yes | Valid Theme foreign key |
| action_title | String | Yes | Non-empty action title |
| description | String | Yes | Action explanation |
| priority | String | Yes | Low, Medium, High or Critical |
| status | String | Yes | Open, In Progress or Resolved |
| source_count | Integer | Yes | Number of linked feedback records |
| negative_percentage | Float | No | Negative feedback percentage |
| threshold_percentage | Float | No | Configured trigger threshold |
| created_at | Datetime | Yes | Valid timestamp |

Automatic action generation uses a negative sentiment threshold of 15%. Priority is determined using the configured negative percentage rules.

## 4. Supporting Entities

The following supporting entities preserve source traceability and data quality information.

### 4.1 ActionItemFeedback

**Purpose:** Links each ActionItem to the exact customer feedback records used as supporting evidence. This enables source-level traceability and allows users to inspect the feedback behind an automatically generated action.

| Field | Type | Required | Validation |
|---|---|---|---|
| mapping_id | String | Yes | Unique mapping identifier; primary key |
| action_id | String | Yes | Foreign key referencing ActionItem |
| source_type | String | Yes | Review, SurveyResponse or SupportMessage |
| source_id | String | Yes | Exact identifier of the source feedback record |
| created_at | Datetime | Yes | Mapping creation timestamp |

**Relationship:** Many-to-many between ActionItem and feedback records, implemented through ActionItemFeedback.

**Reference integrity:** `action_id` is enforced as a database foreign key. `source_id` is a logical reference because it can identify records in different source tables. The application resolves the source using `source_type` and `source_id`.

**Traceability rule:** Automatically generated ActionItems retain links to the feedback records associated with their theme. The negative percentage is calculated using negative feedback records divided by all feedback records for that theme.

### 4.2 ActionItemHistory (Planned)

**Purpose:** Planned functionality to preserve ActionItem status changes instead of overwriting previous states. This entity is not currently implemented.

Proposed fields:

- history_id: Unique history identifier.
- action_id: Foreign key to ActionItem.
- previous_status: Previous lifecycle state.
- new_status: Updated lifecycle state.
- changed_at: Timestamp of the status change.
- changed_by: System or user identifier.
- reason: Explanation for the change.

### 4.3 AnomalyRecord

**Purpose:** Stores detected data quality and exception issues.

| Field | Type | Required | Validation |
|---|---|---|---|
| anomaly_id | String | Yes | Unique anomaly identifier |
| source_type | String | Yes | Review, SurveyResponse or SupportMessage |
| source_id | String | Yes | Identifier of the affected source record |
| anomaly_type | String | Yes | Category of detected anomaly |
| severity | String | Yes | Low, Medium or High |
| description | String | Yes | Explanation of the anomaly |
| details | JSON | No | Additional anomaly information |
| status | String | Yes | Open, Reviewed or Resolved |
| detected_at | Datetime | Yes | Detection timestamp |

**Reference integrity:** `source_id` is a logical reference resolved using `source_type` and `source_id`.

### 4.4 Source Traceability and Privacy

**Source retrieval:** The ActionItem source API retrieves linked feedback using `action_id`, `source_type` and `source_id`. It returns the source type, source identifier, feedback text, sentiment and timestamp.

**PII protection:** Email addresses and Indian phone numbers are masked in feedback text returned by the source API.

- Email addresses are replaced with `[REDACTED EMAIL]`.
- Indian phone numbers are replaced with `[REDACTED PHONE]`.
- Original feedback text remains unchanged in the database.
- Original records are retained for anomaly detection and audit purposes.

**Privacy rule:** API responses must not expose detected email addresses or phone numbers when displaying linked feedback.

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

ActionItem and feedback records have a many-to-many relationship through ActionItemFeedback.

The source identifier in ActionItemFeedback is a logical reference because it can point to different feedback tables based on source_type.

ActionItemHistory is planned and is not included as an implemented database relationship.

## 6. Sentiment and Theme Business Rules

1. Every analysed feedback record receives one of four sentiment labels.
2. Every analysed feedback record receives one of three approved theme labels.
3. Mixed sentiment represents feedback containing both positive and negative signals.
4. The model must not receive ground-truth labels as input.
5. Predictions and ground-truth labels must be stored separately.
6. Confidence scores must be between 0 and 1.
7. Invalid theme assignments must be detected and recorded as anomalies.
8. Feedback source records must retain their original text.
9. PII must be masked in source API responses.

## 7. Data Generation Rules

1. Generate master records before dependent records.
2. Generate valid foreign-key relationships.
3. Use a fixed random seed of 20261022 by default.
4. Generate 30,000 reviews and 20,001 survey responses in the full dataset, including one intentionally injected duplicate survey response.
5. Generate 20,000 support messages in the full dataset.
6. Include multilingual, neutral, mixed, sarcastic and ambiguous examples.
7. Generate valid baseline records before injecting anomalies.
8. Generate ground truth separately from model inputs.
9. Derive totals, scores and statuses from source records.
10. Validate primary keys, foreign keys, allowed values and dates.
11. Preserve the distinction between source feedback, model predictions and ground-truth labels.
12. Export generated records and validation information in the supported formats.

## 8. Required Anomaly Types


| Issue type | Expected detection |
|---|---|
| Contradictory label / Sentiment-text mismatch | Detect disagreement between the stored sentiment label and the review text. Recorded as `SENTIMENT_TEXT_MISMATCH`. |
| Duplicate response | Identify repeated survey submissions |
| PII leakage | Detect email addresses and other personal identifiers |
| Invalid theme | Detect themes outside the approved taxonomy |
| Ground-truth leakage | Prevent evaluation labels from entering model training and prediction through dataset validation and leakage guards. |
| Rating-text mismatch | Identify inconsistencies between review ratings and feedback text |

Detected anomalies are stored in AnomalyRecord and can be reviewed through the anomaly management API.

Ground-truth data is reserved for evaluation and must never be used as prediction input.

## 9. Evaluation

Predictions will be compared with separately maintained ground-truth labels.

### Evaluation Metrics

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

Evaluation will be performed separately for sentiment and theme classification.

The evaluation process must:

1. Load predictions independently from ground-truth labels.
2. Match records using their source identifiers.
3. Calculate classification metrics.
4. Report results for sentiment and theme classification separately.
5. Avoid including ground-truth labels in model training or prediction.

## 10. Reproducibility

The synthetic data generator must:

- Accept a configurable random seed.
- Support starter and full dataset sizes.
- Generate repeatable records using the same seed.
- Maintain unique record identifiers.
- Export CSV and JSON files.
- Produce validation and checksum reports.
- Record dataset configuration and generation details.
- Keep ground-truth data separate from model inputs.

Reproducibility is verified by generating datasets using the same seed and comparing record counts and file checksums.

---

**End of Data Dictionary**
