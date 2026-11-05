import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.ecg_service import ECGService
from app.services.sample_ecg_generator import generate_realistic_ecg
from app.models.all_models import ECGRecord, User
from app.api.deps import get_current_user_optional

router = APIRouter(prefix="/ecg", tags=["ECG Upload & Management"])

@router.post("/upload")
async def upload_ecg(
    file: UploadFile = File(...),
    patient_id: str = Form(..., min_length=2),
    consent_for_research: bool = Form(False),
    sampling_rate: float = Form(250.0),
    session_token: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Accepts ECG uploads (Image, XML, DICOM, CSV, JSON).
    - Preserves original raw uploaded file.
    - Validates file type and size.
    - Executes preprocessing pipeline.
    - Executes AI model service (research demo mode).
    - Supports public users without registration.
    """
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty. Please provide a valid ECG file."
        )

    is_public = current_user is None

    try:
        result = ECGService.process_and_save_ecg(
            db=db,
            file_bytes=file_bytes,
            original_filename=file.filename or "ecg_upload.dat",
            patient_id=patient_id.strip(),
            is_public_session=is_public,
            session_token=session_token,
            consent_for_research=consent_for_research,
            sampling_rate=sampling_rate
        )
        return {
            "success": True,
            "message": "ECG file uploaded and processed successfully.",
            "data": result
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Processing error: {str(e)}")

@router.post("/sample")
def load_sample_ecg(
    patient_id: str = Form("PT-DEMO-01"),
    rhythm_type: str = Form("normal"),  # "normal", "tachycardia", "bradycardia"
    consent_for_research: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Loads a calibrated physiological Lead II sample ECG rhythm for instant
    demonstration of preprocessing and AI analysis pipeline.
    """
    hr_map = {
        "normal": 72.0,
        "tachycardia": 115.0,
        "bradycardia": 50.0
    }
    bpm = hr_map.get(rhythm_type, 72.0)
    synthetic_signal = generate_realistic_ecg(
        duration_seconds=10.0,
        sampling_rate=250.0,
        heart_rate_bpm=bpm,
        noise_amplitude=0.04,
        baseline_wander=True
    )

    # Convert to CSV bytes representation
    csv_lines = ["sample_index,time_sec,lead_ii_mv"]
    for i, val in enumerate(synthetic_signal):
        t = round(i / 250.0, 4)
        csv_lines.append(f"{i},{t},{round(float(val), 4)}")
    csv_bytes = "\n".join(csv_lines).encode("utf-8")

    sample_filename = f"sample_rhythm_{rhythm_type}_{bpm:.0f}bpm.csv"
    is_public = current_user is None

    result = ECGService.process_and_save_ecg(
        db=db,
        file_bytes=csv_bytes,
        original_filename=sample_filename,
        patient_id=patient_id.strip(),
        is_public_session=is_public,
        consent_for_research=consent_for_research,
        sampling_rate=250.0
    )

    return {
        "success": True,
        "message": f"Sample rhythm ({rhythm_type}, {bpm} BPM) generated and processed successfully.",
        "data": result
    }

@router.get("/records/{record_id}")
def get_ecg_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(ECGRecord).filter(ECGRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ECG Record not found.")
    return {
        "id": record.id,
        "patient_id": record.patient_id,
        "original_filename": record.original_filename,
        "file_type": record.file_type,
        "file_size_bytes": record.file_size_bytes,
        "upload_timestamp": record.upload_timestamp.isoformat(),
        "is_public_session": record.is_public_session,
        "consent_for_research": record.consent_for_research
    }
