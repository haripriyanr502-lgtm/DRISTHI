import sys
import json
import datetime
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.database.session import Base, engine, SessionLocal
from app.models.all_models import (
    User, 
    PatientProfile, 
    CaregiverPatientAssignment, 
    ECGRecord, 
    AnalysisResult, 
    PatientAlert
)
from app.services.auth_service import auth_service
from app.services.sample_ecg_generator import generate_realistic_ecg
from app.preprocessing.pipeline import ECGPreprocessingPipeline

def seed():
    print("Seeding DRISTHI Patient and Caretaker Demo Workflow Data...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Clean existing demo data for PT-4082 to ensure idempotency
    db.query(PatientAlert).filter(PatientAlert.patient_id == "PT-4082").delete()
    db.query(AnalysisResult).filter(AnalysisResult.patient_id == "PT-4082").delete()
    db.query(ECGRecord).filter(ECGRecord.patient_id == "PT-4082").delete()
    db.query(CaregiverPatientAssignment).filter(CaregiverPatientAssignment.patient_id == "PT-4082").delete()
    db.query(PatientProfile).filter(PatientProfile.patient_id == "PT-4082").delete()
    db.query(User).filter(User.email.in_(["rajesh.patel@example.com", "priya.patel@example.com"])).delete()
    db.commit()

    # 2. Create Patient User & Profile
    patient_pw = auth_service.hash_password("patient123")
    patient_user = User(
        email="rajesh.patel@example.com",
        hashed_password=patient_pw,
        role="patient",
        full_name="Rajesh Patel",
        phone_number="+91 98765 43210"
    )
    db.add(patient_user)
    db.commit()
    db.refresh(patient_user)

    patient_profile = PatientProfile(
        patient_id="PT-4082",
        user_id=patient_user.id,
        age=58,
        gender="Male",
        medical_history="Mild essential hypertension managed with Telmisartan 40mg once daily. Non-smoker. Occasional exertional fatigue reported during routine morning walks.",
        existing_condition="Hypertension & Occasional Palpitations",
        consent_for_research=True,
        created_at=datetime.datetime.utcnow() - datetime.timedelta(days=7)
    )
    db.add(patient_profile)
    db.commit()
    db.refresh(patient_profile)
    print("   ✓ Created Patient: Rajesh Patel (ID: PT-4082, Age: 58)")

    # 3. Create Caretaker User & Assignment
    caregiver_pw = auth_service.hash_password("caregiver123")
    caregiver_user = User(
        email="priya.patel@example.com",
        hashed_password=caregiver_pw,
        role="caregiver",
        full_name="Priya Patel",
        phone_number="+91 98765 12345"
    )
    db.add(caregiver_user)
    db.commit()
    db.refresh(caregiver_user)

    assignment = CaregiverPatientAssignment(
        caregiver_id=caregiver_user.id,
        patient_id="PT-4082",
        relationship_to_patient="Daughter & Primary Caretaker",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(days=7)
    )
    db.add(assignment)
    db.commit()
    print("   ✓ Created Caretaker: Priya Patel (Assigned to Rajesh Patel PT-4082)")

    # 4. Generate Realistic ECG Records & Analyses
    pipeline = ECGPreprocessingPipeline(sampling_rate=250.0)

    # Record 1: Baseline Normal Sinus Rhythm (5 days ago)
    sig_normal = generate_realistic_ecg(duration_seconds=10.0, sampling_rate=250.0, heart_rate_bpm=72.0, noise_amplitude=0.03, baseline_wander=False)
    prep_normal = pipeline.process_signal(sig_normal)
    wv1 = prep_normal["waveform_preview"]
    sq1 = prep_normal["signal_quality"]
    cm1 = prep_normal["cardiac_metrics"]

    rec1 = ECGRecord(
        patient_id="PT-4082",
        original_filename="rajesh_baseline_rhythm_strip_lead_ii.csv",
        stored_filename="seed_rec_1_normal.csv",
        file_type="numerical",
        file_path="data/sample/seed_rec_1_normal.csv",
        file_size_bytes=24800,
        is_public_session=False,
        consent_for_research=True,
        upload_timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=4, hours=3)
    )
    db.add(rec1)
    db.commit()
    db.refresh(rec1)

    analysis1 = AnalysisResult(
        ecg_record_id=rec1.id,
        patient_id="PT-4082",
        status="completed_demo",
        is_simulated_demo=True,
        model_name="DRISTHI Research Prototype (Candidate 1D-ResNet Benchmarking)",
        model_version="0.1.0-alpha",
        signal_quality_score=0.96,
        noise_level="Low",
        baseline_wander_detected=False,
        sampling_rate_hz=250.0,
        duration_seconds=10.0,
        r_peaks_detected_count=cm1["r_peak_count"],
        estimated_heart_rate_bpm=72.0,
        prediction_label="Normal Sinus Rhythm (Demonstration Reference)",
        confidence_score=0.94,
        classification_categories_json=json.dumps([
            "Normal Sinus Rhythm", "Atrial Fibrillation", "Premature Ventricular Contractions (PVC)",
            "Sinus Tachycardia", "Sinus Bradycardia", "Ventricular Bigeminy"
        ]),
        observations_json=json.dumps([
            "Regular sinus P-wave morphology preceding every QRS complex.",
            "Normal PR interval duration (~160 ms).",
            "Mean Heart Rate calculated at 72.0 BPM (within normal resting envelope 60-100 BPM).",
            "Optimal Signal-to-Noise Ratio (SNR 0.96) with minimal baseline drift."
        ]),
        original_signal_json=json.dumps(wv1["original_signal"]),
        processed_signal_json=json.dumps(wv1["processed_signal"]),
        created_at=datetime.datetime.utcnow() - datetime.timedelta(days=4, hours=3)
    )
    db.add(analysis1)
    db.commit()

    # Record 2: Exertional Tachycardia episode (14 hours ago)
    sig_tachy = generate_realistic_ecg(duration_seconds=10.0, sampling_rate=250.0, heart_rate_bpm=114.0, noise_amplitude=0.06, baseline_wander=True)
    prep_tachy = pipeline.process_signal(sig_tachy)
    wv2 = prep_tachy["waveform_preview"]
    sq2 = prep_tachy["signal_quality"]
    cm2 = prep_tachy["cardiac_metrics"]

    rec2 = ECGRecord(
        patient_id="PT-4082",
        original_filename="rajesh_exertion_post_walk_palpitation.csv",
        stored_filename="seed_rec_2_tachy.csv",
        file_type="numerical",
        file_path="data/sample/seed_rec_2_tachy.csv",
        file_size_bytes=24800,
        is_public_session=False,
        consent_for_research=True,
        upload_timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=14)
    )
    db.add(rec2)
    db.commit()
    db.refresh(rec2)

    analysis2 = AnalysisResult(
        ecg_record_id=rec2.id,
        patient_id="PT-4082",
        status="completed_demo",
        is_simulated_demo=True,
        model_name="DRISTHI Research Prototype (Candidate 1D-ResNet Benchmarking)",
        model_version="0.1.0-alpha",
        signal_quality_score=0.82,
        noise_level="Moderate",
        baseline_wander_detected=True,
        sampling_rate_hz=250.0,
        duration_seconds=10.0,
        r_peaks_detected_count=cm2["r_peak_count"],
        estimated_heart_rate_bpm=114.0,
        prediction_label="Sinus Tachycardia (Demonstration Reference)",
        confidence_score=0.91,
        classification_categories_json=json.dumps([
            "Normal Sinus Rhythm", "Atrial Fibrillation", "Premature Ventricular Contractions (PVC)",
            "Sinus Tachycardia", "Sinus Bradycardia", "Ventricular Bigeminy"
        ]),
        observations_json=json.dumps([
            "Elevated ventricular rate: Calculated Heart Rate = 114.0 BPM (> 100 BPM threshold).",
            "Noticeable low-frequency baseline drift detected due to post-exercise hyperpnea (respiration).",
            "Zero-phase 0.67 Hz digital Butterworth filter successfully restored isoelectric baseline.",
            "QRS complexes remain narrow (< 100 ms), indicating supraventricular origin."
        ]),
        original_signal_json=json.dumps(wv2["original_signal"]),
        processed_signal_json=json.dumps(wv2["processed_signal"]),
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=14)
    )
    db.add(analysis2)
    db.commit()
    print("   ✓ Created 2 ECG Records & Conditioned Analyses for PT-4082")

    # 5. Create Caregiver Alerts
    alert1 = PatientAlert(
        patient_id="PT-4082",
        title="Sinus Tachycardia Advisory (114 BPM)",
        severity="warning",
        message="Patient heart rate recorded at 114 BPM during 10-second post-walk recording. Exceeds standard resting threshold of 100 BPM (Simulated Demonstration Advisory).",
        is_hardware_simulation=True,
        is_acknowledged=False,
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=14)
    )
    db.add(alert1)

    alert2 = PatientAlert(
        patient_id="PT-4082",
        title="Baseline Wander Digital Conditioning Log",
        severity="info",
        message="Respiratory motion artifact detected on Lead II strip. Zero-phase 0.67 Hz digital filter applied automatically.",
        is_hardware_simulation=True,
        is_acknowledged=True,
        acknowledged_by="Priya Patel",
        acknowledged_at=datetime.datetime.utcnow() - datetime.timedelta(hours=12),
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=14, minutes=5)
    )
    db.add(alert2)
    db.commit()
    print("   ✓ Created Caregiver Alerts (1 Pending Acknowledgement, 1 Acknowledged)")

    db.close()
    print("\n==================================================")
    print("DEMO WORKFLOW SEED COMPLETE!")
    print("Patient: Rajesh Patel (PT-4082, rajesh.patel@example.com / patient123)")
    print("Caretaker: Priya Patel (priya.patel@example.com / caregiver123)")
    print("==================================================")

if __name__ == "__main__":
    seed()

