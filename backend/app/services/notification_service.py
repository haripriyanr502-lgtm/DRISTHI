import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.all_models import PatientAlert, PatientProfile, CaregiverPatientAssignment

class NotificationService:
    @staticmethod
    def get_patient_alerts(db: Session, patient_id: str) -> List[PatientAlert]:
        return db.query(PatientAlert).filter(PatientAlert.patient_id == patient_id).order_by(PatientAlert.created_at.desc()).all()

    @staticmethod
    def get_caregiver_dashboard_data(db: Session, caregiver_id: int) -> Dict[str, Any]:
        """
        Retrieves assigned patient information, monitoring status, alerts,
        and hardware status notice.
        """
        assignments = db.query(CaregiverPatientAssignment).filter(
            CaregiverPatientAssignment.caregiver_id == caregiver_id
        ).all()

        patient_ids = [a.patient_id for a in assignments]
        
        # If no assignments yet, find or assign a demo profile for evaluation
        if not patient_ids:
            profile = db.query(PatientProfile).first()
            if profile:
                assignment = CaregiverPatientAssignment(
                    caregiver_id=caregiver_id,
                    patient_id=profile.patient_id,
                    relationship_to_patient="Primary Caregiver"
                )
                db.add(assignment)
                db.commit()
                patient_ids = [profile.patient_id]

        patients = db.query(PatientProfile).filter(PatientProfile.patient_id.in_(patient_ids)).all()
        alerts = db.query(PatientAlert).filter(PatientAlert.patient_id.in_(patient_ids)).order_by(PatientAlert.created_at.desc()).all()

        # If no alerts exist yet, seed a realistic sample alert clearly marked as simulated
        if not alerts and patients:
            sample_alert = PatientAlert(
                patient_id=patients[0].patient_id,
                title="Tachycardia Rate Advisory (Simulated)",
                severity="warning",
                message="Heart rate exceeded 105 BPM during 10-second monitoring window (Simulated demo event).",
                is_hardware_simulation=True,
                is_acknowledged=False,
                created_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=14)
            )
            db.add(sample_alert)
            db.commit()
            db.refresh(sample_alert)
            alerts = [sample_alert]

        return {
            "assigned_patients": [
                {
                    "patient_id": p.patient_id,
                    "age": p.age,
                    "gender": p.gender or "Unspecified",
                    "existing_condition": p.existing_condition or "None recorded",
                    "medical_history": p.medical_history or "None recorded",
                    "hardware_monitoring_status": "Staged (Awaiting ESP32 + AD8232 Telemetry)",
                    "last_active": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
                }
                for p in patients
            ],
            "alerts": [
                {
                    "id": a.id,
                    "patient_id": a.patient_id,
                    "title": a.title,
                    "severity": a.severity,
                    "message": a.message,
                    "is_hardware_simulation": a.is_hardware_simulation,
                    "is_acknowledged": a.is_acknowledged,
                    "acknowledged_by": a.acknowledged_by,
                    "acknowledged_at": a.acknowledged_at.isoformat() if a.acknowledged_at else None,
                    "created_at": a.created_at.isoformat()
                }
                for a in alerts
            ],
            "hardware_integration_notice": {
                "sensor": "AD8232 Single-Lead Heart Rate Monitor Analog Front End",
                "microcontroller": "ESP32 Dual-Core Wi-Fi / BLE SoC",
                "telemetry_protocol": "WebSocket / MQTT / HTTP POST Telemetry Stream",
                "status": "Architecture Ready — Live Telemetry Awaiting Device Provisioning",
                "simulation_mode": True
            }
        }

    @staticmethod
    def acknowledge_alert(db: Session, alert_id: int, caregiver_name: str) -> Optional[PatientAlert]:
        alert = db.query(PatientAlert).filter(PatientAlert.id == alert_id).first()
        if not alert:
            return None
        alert.is_acknowledged = True
        alert.acknowledged_by = caregiver_name
        alert.acknowledged_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(alert)
        return alert

notification_service = NotificationService()
