
from app.db.database import Base, engine
import app.models


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("InsightPulse AI database initialized successfully!")


if __name__ == "__main__":
    initialize_database()
