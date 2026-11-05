from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.models.all_models import PatientProfile, User
from app.schemas.all_schemas import PatientProfileCreate, PatientProfileUpdate, PatientProfileResponse
from app.api.deps import get_current_user_optional
from app.services.patient_service import patient_service

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/{patient_id}", response_model=PatientProfileResponse)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(PatientProfile).filter(PatientProfile.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID '{patient_id}' not found."
        )
    return patient

@router.post("", response_model=PatientProfileResponse)
def create_or_update_patient(
    profile_in: PatientProfileCreate, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    patient = db.query(PatientProfile).filter(PatientProfile.patient_id == profile_in.patient_id).first()
    
    if patient:
        # Update existing
        patient.age = profile_in.age
        if profile_in.gender is not None:
            patient.gender = profile_in.gender
        if profile_in.medical_history is not None:
            patient.medical_history = profile_in.medical_history
        if profile_in.existing_condition is not None:
            patient.existing_condition = profile_in.existing_condition
        if profile_in.consent_for_research is not None:
            patient.consent_for_research = profile_in.consent_for_research
        if user_id and not patient.user_id:
            patient.user_id = user_id
    else:
        # Create new
        patient = PatientProfile(
            patient_id=profile_in.patient_id,
            user_id=user_id,
            age=profile_in.age,
            gender=profile_in.gender,
            medical_history=profile_in.medical_history,
            existing_condition=profile_in.existing_condition,
            consent_for_research=profile_in.consent_for_research or False
        )
        db.add(patient)
    
    db.commit()
    db.refresh(patient)
    return patient

@router.get("/{patient_id}/records")
def get_patient_ecg_records(patient_id: str, db: Session = Depends(get_db)):
    """Returns uploaded records, preprocessing summary, and analysis history."""
    records = patient_service.get_patient_records(db, patient_id)
    return {
        "patient_id": patient_id,
        "total_records": len(records),
        "records": records
    }
