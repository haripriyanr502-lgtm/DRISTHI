import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

def run_smoke_tests():
    print("==================================================")
    print("DRISTHI BACKEND VERIFICATION & SMOKE TEST SUITE")
    print("==================================================")

    # 1. Test database & model schema initialization
    print("\n[1/6] Initializing Database & SQLAlchemy Models...")
    from app.database.session import Base, engine, SessionLocal
    import app.models
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    print("   ✓ SQLite database initialized successfully.")

    # 2. Test Preprocessing Pipeline
    print("\n[2/6] Testing ECG Preprocessing Pipeline...")
    from app.services.sample_ecg_generator import generate_realistic_ecg
    from app.preprocessing.pipeline import ECGPreprocessingPipeline

    signal = generate_realistic_ecg(duration_seconds=10.0, sampling_rate=250.0, heart_rate_bpm=75.0)
    pipeline = ECGPreprocessingPipeline(sampling_rate=250.0)
    proc_result = pipeline.process_signal(signal)
    
    sq = proc_result["signal_quality"]
    cm = proc_result["cardiac_metrics"]
    print(f"   ✓ Sampling Rate: {proc_result['pipeline_config']['sampling_rate_hz']} Hz")
    print(f"   ✓ Signal Quality Score: {sq['quality_score']} (Noise Level: {sq['noise_level']})")
    print(f"   ✓ Detected R-Peaks: {cm['r_peak_count']}")
    print(f"   ✓ Calculated Heart Rate: {cm['estimated_hr_bpm']} BPM")
    assert cm["r_peak_count"] > 5, "Expected at least 5 R-peaks in 10-second ECG"
    assert cm["estimated_hr_bpm"] is not None, "Expected valid HR computation"

    # 3. Test AI Service Manager & Demonstration Model
    print("\n[3/6] Testing AI Service Staging Layer...")
    from app.ai.model_service import ai_service
    ai_status = ai_service.get_model_status()
    print(f"   ✓ AI Status: {ai_status['status_description']}")
    assert "Research Demonstration" in ai_status["status_description"]

    demo_pred = ai_service.run_inference(signal, sampling_rate=250.0)
    print(f"   ✓ Staged Prediction: {demo_pred['prediction_label']}")
    print(f"   ✓ Demonstration Flag: is_simulated_demo={demo_pred['is_simulated_demo']}")
    assert demo_pred["is_simulated_demo"] is True, "Must be flagged as simulated demo"

    # 4. Test User & Patient Account Flow
    print("\n[4/6] Testing Auth & Patient Profile Services...")
    from app.services.auth_service import auth_service
    from app.models.all_models import User, PatientProfile
    
    # Check password hashing & token generation
    test_pw = "MedicalGradeSecret2026!"
    hashed = auth_service.hash_password(test_pw)
    assert auth_service.verify_password(test_pw, hashed), "Password verification failed"
    token = auth_service.create_access_token({"sub": "1", "role": "patient"})
    payload = auth_service.decode_access_token(token)
    assert payload is not None and payload.get("sub") == "1", "Token validation failed"
    print("   ✓ Password hashing and JWT generation operational.")

    # 5. Test ECG Record Ingestion & Analysis Persistence
    print("\n[5/6] Testing ECG Service & Full Persistence Flow...")
    from app.services.ecg_service import ECGService
    
    csv_sample = "index,time,lead_ii\n" + "\n".join([f"{i},{round(i/250,3)},{round(float(v),4)}" for i, v in enumerate(signal)])
    ingest_result = ECGService.process_and_save_ecg(
        db=db,
        file_bytes=csv_sample.encode("utf-8"),
        original_filename="clinical_rhythm_strip.csv",
        patient_id="PT-TEST-01",
        is_public_session=False,
        consent_for_research=False,
        sampling_rate=250.0
    )
    print(f"   ✓ Created ECG Record #{ingest_result['record_id']}")
    print(f"   ✓ Created Analysis Result #{ingest_result['analysis_id']}")
    
    detail = ECGService.get_analysis_detail(db, ingest_result["analysis_id"])
    assert detail is not None, "Failed to retrieve saved analysis"
    assert len(detail["waveform"]["original_signal"]) > 0, "Original signal must be preserved"
    assert len(detail["waveform"]["processed_signal"]) > 0, "Processed signal must be preserved"
    print(f"   ✓ Preserved Original Data: {len(detail['waveform']['original_signal'])} samples")
    print(f"   ✓ Generated Processed Data: {len(detail['waveform']['processed_signal'])} samples")

    # 6. Test Caregiver Dashboard & Hardware Integration Staging
    print("\n[6/6] Testing Caregiver Dashboard & Hardware Staging...")
    from app.services.notification_service import notification_service
    cg_user = db.query(User).filter(User.role == "caregiver").first()
    if not cg_user:
        cg_user = User(
            email="caregiver.demo@dristhi.health",
            hashed_password=hashed,
            role="caregiver",
            full_name="Sarah Jenkins (Caregiver)"
        )
        db.add(cg_user)
        db.commit()
        db.refresh(cg_user)

    cg_data = notification_service.get_caregiver_dashboard_data(db, cg_user.id)
    print(f"   ✓ Assigned Patients: {len(cg_data['assigned_patients'])}")
    print(f"   ✓ Active Alerts: {len(cg_data['alerts'])}")
    print(f"   ✓ Hardware Telemetry: {cg_data['hardware_integration_notice']['status']}")

    db.close()
    print("\n==================================================")
    print("ALL MODULE VERIFICATION CHECKS PASSED (6/6)!")
    print("==================================================")

if __name__ == "__main__":
    run_smoke_tests()
