# InsightPulse AI — Customer Feedback Intelligence Platform

An AI-powered customer feedback intelligence platform that combines reviews, survey responses, and support messages to identify customer sentiment, discover feedback themes, detect data-quality issues, and generate actionable recommendations.

## 1. Project Overview

Organizations receive customer feedback through multiple channels. Analyzing this information manually can make it difficult to identify recurring problems and prioritize improvements.

InsightPulse AI brings feedback from multiple sources into one platform and provides:

- Customer feedback aggregation
- Sentiment classification
- Theme-based feedback analysis
- Customer feedback analytics
- Data-quality anomaly detection
- Automated action-item generation
- Source-level feedback traceability
- AI-generated feedback insights
- Interactive analytics dashboard

## 2. Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React 19, Vite |
| Backend | Python, FastAPI |
| Database | SQLite, SQLAlchemy |
| Machine Learning | scikit-learn, TF-IDF, Logistic Regression |
| Data Processing | Pandas, NumPy |
| AI Insights | Ollama, Llama 3.2 |
| API Documentation | FastAPI Swagger UI |

## 3. System Architecture

```text
Customer Feedback Sources
          |
          v
+-----------------------------+
| Reviews                     |
| Survey Responses            |
| Support Messages            |
+-----------------------------+
          |
          v
+-----------------------------+
| FastAPI Backend             |
|                             |
| Data Management             |
| Sentiment Analysis          |
| Theme Detection             |
| Anomaly Detection           |
| Analytics                   |
| Action Item Generation      |
+-----------------------------+
          |
          v
+-----------------------------+
| SQLite Database             |
|                             |
| Customers                   |
| Products                    |
| Channels                    |
| Reviews                     |
| Survey Responses            |
| Support Messages            |
| Themes                      |
| Action Items                |
| Anomaly Records             |
+-----------------------------+
          |
          v
+-----------------------------+
| React Dashboard             |
|                             |
| Feedback Analytics          |
| Sentiment Distribution      |
| Theme Analysis              |
| AI Insights                 |
| Action Items                |
| Source Feedback             |
+-----------------------------+
```

## 4. Feedback Classification

### Sentiment Categories

The platform supports four sentiment labels:

- Positive
- Neutral
- Negative
- Mixed

### Required Feedback Themes

- Performance
- Customer Support
- Feature Request

## 5. Synthetic Dataset

The project includes a reproducible synthetic customer feedback dataset.

The full dataset contains:

| Dataset | Records |
|---|---:|
| Customers | 5,000 |
| Products | 5 |
| Channels | 5 |
| Surveys | 100 |
| Reviews | 30,000 |
| Survey Responses | 20,001 |
| Support Messages | 20,000 |
| **Total Feedback Records** | **70,001** |

The survey dataset includes one deliberately injected duplicate-submission case for anomaly testing.

### Dataset Generation

Generate the full synthetic dataset:

```bash
python backend/scripts/generate_synthetic_data.py --scale full
```

The generator uses a fixed seed for reproducibility.

Generated files are stored separately from ground-truth evaluation data:

- `data/generated_full/`
- `data/ground_truth_full/`
- `data/manifests_full/`

Ground-truth data is reserved for evaluation and is not intended to be used as model input.

## 6. Machine Learning

### Sentiment Analysis

The sentiment classification pipeline uses:

- TF-IDF text vectorization
- Unigram and bigram features
- Logistic Regression
- Stratified train-test splitting

Prepare the training dataset:

```bash
python ml/prepare_dataset.py
```

Train and evaluate the model:

```bash
python ml/sentiment_model.py
```

The latest recorded test accuracy during development was **62.07%**. This result is based on a small set of unique synthetic text examples and should not be interpreted as real-world model performance.

The trained model is saved locally as:

`ml/sentiment_pipeline.joblib`

The model file is generated during training and is not required to be committed to GitHub.

## 7. Anomaly Detection

The platform includes anomaly detection for identifying data-quality issues such as:

- Duplicate submissions
- Personally identifiable information (PII)
- Invalid feedback themes
- Rating and feedback-text mismatches

Anomaly records can be reviewed through the backend API and dashboard.

## 8. Action Item Generation and Traceability

InsightPulse AI generates action recommendations based on negative feedback patterns.

The action-item workflow includes:

1. Group feedback by theme.
2. Calculate negative feedback percentages.
3. Compare results against the configured threshold.
4. Generate recommendations when the threshold is exceeded.
5. Link feedback records to their corresponding action items.
6. Retrieve source feedback for investigation.

The automatic action-generation threshold is currently 15%.

## 9. Project Structure

```text
insightpulse-ai/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── scripts/
│   │   └── generate_synthetic_data.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── ml/
│   ├── import_feedback_to_database.py
│   ├── prepare_dataset.py
│   ├── run_theme_detection.py
│   └── sentiment_model.py
│
├── data/
│   ├── generated/
│   ├── generated_full/
│   ├── ground_truth/
│   ├── ground_truth_full/
│   └── manifests_full/
│
├── docs/
│   └── data_dictionary.md
│
└── README.md
```

## 10. Installation and Setup

### Prerequisites

- Python 3.12+
- Node.js and npm
- Git

### Backend Setup

From the project root:

```bash
python -m venv backend/.venv
```

Activate the virtual environment in Git Bash:

```bash
source backend/.venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Start the FastAPI backend:

```bash
python -m uvicorn app.main:app --reload --app-dir backend
```

Backend URL:

`http://127.0.0.1:8000`

Swagger API documentation:

`http://127.0.0.1:8000/docs`

### Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

`http://localhost:5173`

### Production Build

From the frontend directory:

```bash
npm run build
```

## 11. Database

The backend uses SQLite with SQLAlchemy.

The database is configured at:

`backend/insightpulse.db`

The application includes database models for customers, products, channels, surveys, reviews, survey responses, support messages, themes, sentiment labels, anomaly records, and action items.

## 12. API Features

The FastAPI backend provides endpoints for:

- Customer management
- Product management
- Review management
- Survey management
- Survey response management
- Support message management
- Sentiment prediction
- Theme detection
- Feedback analytics
- Anomaly detection
- Action-item management
- Action-item source feedback
- AI-generated insights

For available endpoints and request schemas, open the Swagger documentation at `/docs`.

## 13. Data Privacy and Evaluation

- Synthetic data is used for project development and testing.
- PII detection and redaction are included in the feedback workflow.
- Ground-truth evaluation files are kept separate from model-training inputs.
- Deliberately injected edge cases are used to test data-quality and leakage safeguards.

## 14. Project Objective

InsightPulse AI demonstrates how machine learning, natural language processing, backend APIs, and interactive dashboards can work together to transform unstructured customer feedback into structured insights and actionable recommendations.

---

**Project:** InsightPulse AI — Customer Feedback Intelligence Platform  
**Repository:** https://github.com/nikhithabhandary08/insightpulse-ai