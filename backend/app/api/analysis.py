from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.ecg_service import ECGService
from app.ai.model_service import ai_service

router = APIRouter(prefix="/analysis", tags=["ECG Analysis Results"])

@router.get("/status")
def get_ai_service_status():
    """
    Returns AI integration layer status, research benchmark datasets under review,
    and supported classification classes.
    """
    return ai_service.get_model_status()

@router.get("/{analysis_id}")
def get_analysis_results(analysis_id: int, db: Session = Depends(get_db)):
    """
    Retrieves complete analysis report for an ECG record:
    - Patient ID & File metadata
    - Signal quality metrics (SNR, Noise level, Baseline wander)
    - Heart rate & R-peak measurements
    - Model prediction status & demonstration disclosure
    - Original vs Processed waveform data for side-by-side visualization
    """
    data = ECGService.get_analysis_detail(db, analysis_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis result #{analysis_id} not found."
        )
    return data
