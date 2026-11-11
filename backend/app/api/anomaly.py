
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.services.anomaly_service import run_anomaly_detection
from app.models.anomaly_record import AnomalyRecord


router = APIRouter(
    prefix="/anomalies",
    tags=["Anomaly Detection"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/scan")
def scan_anomalies(db: Session = Depends(get_db)):
    """Scan feedback records and detect anomalies."""

    try:
        return run_anomaly_detection(db)

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Anomaly detection failed: {str(error)}",
        )


@router.get("/")
def get_anomalies(db: Session = Depends(get_db)):
    """Retrieve detected anomalies."""

    return (
        db.query(AnomalyRecord)
        .order_by(AnomalyRecord.detected_at.desc())
        .all()
    )


@router.get("/summary")
def get_anomaly_summary(db: Session = Depends(get_db)):
    """Get anomaly counts grouped by type and severity."""

    records = db.query(AnomalyRecord).all()

    summary = {
        "total_anomalies": len(records),
        "by_type": {},
        "by_severity": {},
        "by_status": {},
    }

    for record in records:
        summary["by_type"][record.anomaly_type] = (
            summary["by_type"].get(record.anomaly_type, 0) + 1
        )

        summary["by_severity"][record.severity] = (
            summary["by_severity"].get(record.severity, 0) + 1
        )

        summary["by_status"][record.status] = (
            summary["by_status"].get(record.status, 0) + 1
        )

    return summary
