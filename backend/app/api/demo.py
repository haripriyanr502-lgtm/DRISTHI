import json
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database.session import get_db
from app.models.all_models import PatientProfile, ECGRecord, AnalysisResult, PatientAlert
from app.demo.synthetic_ecg_catalog import (
    DEMO_CASES,
    get_demo_case_by_id,
    DEMO_DATA_DISCLAIMER,
    MOCK_RESULT_DISCLAIMER
)

router = APIRouter(prefix="/demo", tags=["Temporary Demo Data Mode"])

@router.get("/cases")
def list_demo_cases():
    """
    Returns the catalog of synthetic sample ECG cases available for testing.
    All cases are strictly labelled: DEMO DATA – NOT A REAL PATIENT RECORD.
    """
    summaries = []
    for c in DEMO_CASES:
        summaries.append({
            "case_id": c["case_id"],
            "title": c["title"],
            "rhythm_type": c["rhythm_type"],
            "demo_watermark": c["demo_watermark"],
            "disclaimer": c["disclaimer"],
            "patient_id": c["patient"]["patient_id"],
            "patient_age": c["patient"]["age"],
            "patient_gender": c["patient"]["gender"],
            "existing_condition": c["patient"]["existing_condition"],
            "heart_rate_bpm": c["mock_analysis"]["heart_rate_bpm"],
            "prediction_label": c["mock_analysis"]["prediction_label"],
            "signal_quality_score": c["mock_analysis"]["signal_quality_score"]
        })
    return {
        "demo_mode": True,
        "watermark": DEMO_DATA_DISCLAIMER,
        "policy": "Temporary DEMO DATA mode using synthetic sample signals for workflow and report testing.",
        "cases_count": len(summaries),
        "cases": summaries
    }

@router.get("/cases/{case_id}")
def get_demo_case_detail(case_id: str):
    """
    Retrieves full synthetic ECG waveform data, sample patient profile,
    and mock report for a specific demo case.
    """
    case = get_demo_case_by_id(case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Demo case '{case_id}' not found."
        )
    return {
        "success": True,
        "demo_mode": True,
        "watermark": DEMO_DATA_DISCLAIMER,
        "data": case
    }

@router.post("/load/{case_id}")
def load_demo_case_into_session(case_id: str, db: Session = Depends(get_db)):
    """
    Persists a synthetic demo case into the database to allow full
    end-to-end testing of the report interface, patient records, and dashboard.
    All created database records are permanently flagged with is_simulated_demo = True
    and clearly branded with the DEMO DATA watermark.
    """
    case = get_demo_case_by_id(case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Demo case '{case_id}' not found."
        )

    p_data = case["patient"]
    r_data = case["recording"]
    a_data = case["mock_analysis"]
    wf_data = case["waveform"]

    # 1. Get or create sample demo patient profile
    pid = p_data["patient_id"]
    patient = db.query(PatientProfile).filter(PatientProfile.patient_id == pid).first()
    if not patient:
        patient = PatientProfile(
            patient_id=pid,
            age=p_data["age"],
            gender=p_data["gender"],
            medical_history=f"[{DEMO_DATA_DISCLAIMER}] {p_data['medical_history']}",
            existing_condition=p_data["existing_condition"],
            consent_for_research=False
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)

    # 2. Persist ECG Record
    record = ECGRecord(
        patient_id=pid,
        original_filename=r_data["original_filename"],
        stored_filename=f"synthetic_{case_id.lower()}.csv",
        file_type="numerical",
        file_path=f"data/sample/{r_data['original_filename']}",
        file_size_bytes=24800,
        is_public_session=False,
        consent_for_research=False,
        upload_timestamp=datetime.datetime.utcnow()
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # 3. Persist Mock Analysis Result
    obs = [DEMO_DATA_DISCLAIMER] + a_data["observations"]
    analysis = AnalysisResult(
        ecg_record_id=record.id,
        patient_id=pid,
        status="completed_demo",
        is_simulated_demo=True,
        model_name="DRISTHI Synthetic Waveform Demo Pipeline",
        model_version="0.1.0-demo",
        signal_quality_score=a_data["signal_quality_score"],
        noise_level=a_data["noise_level"],
        baseline_wander_detected=a_data["baseline_wander_detected"],
        sampling_rate_hz=r_data["sampling_rate_hz"],
        duration_seconds=r_data["duration_seconds"],
        r_peaks_detected_count=len(wf_data["r_peak_indices"]),
        estimated_heart_rate_bpm=a_data["heart_rate_bpm"],
        prediction_label=f"{a_data['prediction_label']}",
        confidence_score=a_data["confidence_score"],
        classification_categories_json=json.dumps([
            "Normal Sinus Rhythm", "Sinus Tachycardia", "Sinus Bradycardia",
            "Premature Ventricular Contractions (PVC)", "Atrial Fibrillation"
        ]),
        observations_json=json.dumps(obs),
        original_signal_json=json.dumps(wf_data["original_signal"]),
        processed_signal_json=json.dumps(wf_data["processed_signal"]),
        created_at=datetime.datetime.utcnow()
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "success": True,
        "demo_mode": True,
        "watermark": DEMO_DATA_DISCLAIMER,
        "disclaimer": MOCK_RESULT_DISCLAIMER,
        "message": f"Demo case '{case['title']}' loaded into session.",
        "record_id": record.id,
        "patient_id": pid,
        "analysis_id": analysis.id,
        "waveform": wf_data,
        "patient": p_data,
        "mock_analysis": a_data
    }

