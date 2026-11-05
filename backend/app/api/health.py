from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.session import get_db
from app.config import settings
from app.ai.model_service import ai_service
import os

router = APIRouter(tags=["Health & Diagnostics"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "operational",
        "app_name": settings.PROJECT_NAME,
        "tagline": settings.PROJECT_TAGLINE,
        "version": "1.0.0-initial",
        "database": db_status,
        "ai_subsystem": ai_service.get_model_status(),
        "hardware_subsystem": "Awaiting ESP32 / AD8232 Hardware Link",
        "storage": {
            "raw_dir": str(settings.UPLOAD_RAW_DIR),
            "raw_dir_exists": settings.UPLOAD_RAW_DIR.exists()
        }
    }
