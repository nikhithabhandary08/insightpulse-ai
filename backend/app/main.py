
from fastapi import FastAPI

from app.api.customer import router as customer_router
from app.api.product import router as product_router
from app.api.review import router as review_router
from app.api.survey import router as survey_router
from app.api.survey_response import router as survey_response_router
from app.api.support import router as support_router
from app.api.sentiment import router as sentiment_router
from app.api.theme import router as theme_router
from app.api.analytics import router as analytics_router

app = FastAPI(
    title="InsightPulse AI",
    description="Customer Feedback Intelligence Platform",
    version="1.0.0"
)

# Register API routes
app.include_router(customer_router)
app.include_router(product_router)
app.include_router(review_router)
app.include_router(survey_router)
app.include_router(survey_response_router)
app.include_router(support_router)
app.include_router(sentiment_router)
app.include_router(theme_router)
app.include_router(analytics_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to InsightPulse AI",
        "status": "Running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
