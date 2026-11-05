from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.all_models import PatientProfile, ECGRecord, AnalysisResult

class PatientService:
    @staticmethod
    def get_or_create_patient(
        db: Session,
        patient_id: str,
        age: int = 45,
        gender: Optional[str] = None,
        medical_history: Optional[str] = None,
        existing_condition: Optional[str] = None,
        consent_for_research: bool = False,
        user_id: Optional[int] = None
    ) -> PatientProfile:
        patient = db.query(PatientProfile).filter(PatientProfile.patient_id == patient_id).first()
        if not patient:
            patient = PatientProfile(
                patient_id=patient_id,
                user_id=user_id,
                age=age,
                gender=gender,
                medical_history=medical_history,
                existing_condition=existing_condition,
                consent_for_research=consent_for_research
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
        elif user_id and not patient.user_id:
            patient.user_id = user_id
            db.commit()
            db.refresh(patient)
        return patient

    @staticmethod
    def get_patient_records(db: Session, patient_id: str) -> List[Dict[str, Any]]:
        """Retrieves patient's uploaded ECG records with analysis summary."""
        records = db.query(ECGRecord).filter(ECGRecord.patient_id == patient_id).order_by(ECGRecord.upload_timestamp.desc()).all()
        result = []
        for r in records:
            analysis = db.query(AnalysisResult).filter(AnalysisResult.ecg_record_id == r.id).first()
            result.append({
                "id": r.id,
                "patient_id": r.patient_id,
                "original_filename": r.original_filename,
                "file_type": r.file_type,
                "file_size_bytes": r.file_size_bytes,
                "is_public_session": r.is_public_session,
                "consent_for_research": r.consent_for_research,
                "upload_timestamp": r.upload_timestamp.isoformat(),
                "has_analysis": analysis is not None,
                "analysis_id": analysis.id if analysis else None,
                "status": analysis.status if analysis else "pending",
                "prediction_label": analysis.prediction_label if analysis else "Pending Analysis",
                "confidence_score": analysis.confidence_score if analysis else None,
                "heart_rate_bpm": analysis.estimated_heart_rate_bpm if analysis else None,
                "is_simulated_demo": analysis.is_simulated_demo if analysis else False
            })
        return result

patient_service = PatientService()
