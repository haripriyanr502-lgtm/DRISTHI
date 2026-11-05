import os
import json
import uuid
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import numpy as np
from sqlalchemy.orm import Session

from app.config import settings, UPLOAD_RAW_DIR
from app.models.all_models import ECGRecord, AnalysisResult, PatientProfile
from app.preprocessing.pipeline import ECGPreprocessingPipeline
from app.preprocessing.image_extractor import ECGImageExtractor
from app.ai.model_service import ai_service
from app.services.sample_ecg_generator import generate_realistic_ecg

class ECGService:
    @staticmethod
    def validate_file(filename: str, file_size: int) -> Tuple[bool, str, str]:
        """
        Validates file size and extension.
        Returns: (is_valid, error_message, file_category)
        """
        if file_size > settings.MAX_FILE_SIZE_BYTES:
            return False, f"File size ({round(file_size / (1024*1024), 2)} MB) exceeds limit of 25 MB.", ""

        ext = Path(filename).suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            return False, f"Unsupported file format '{ext}'. Supported: Images (.png, .jpg), XML (.xml), DICOM (.dcm), Numerical (.csv, .json).", ""

        if ext in [".png", ".jpg", ".jpeg"]:
            category = "image"
        elif ext == ".xml":
            category = "xml"
        elif ext == ".dcm":
            category = "dicom"
        else:
            category = "numerical"

        return True, "", category

    @classmethod
    def process_and_save_ecg(
        cls,
        db: Session,
        file_bytes: bytes,
        original_filename: str,
        patient_id: str,
        is_public_session: bool = False,
        session_token: Optional[str] = None,
        consent_for_research: bool = False,
        sampling_rate: float = 250.0
    ) -> Dict[str, Any]:
        """
        Saves original uploaded file, runs preprocessing, executes AI demonstration pipeline,
        and persists records to database.
        """
        # Ensure patient profile exists in database
        patient = db.query(PatientProfile).filter(PatientProfile.patient_id == patient_id).first()
        if not patient:
            # Auto-create basic profile if public user or quick upload
            patient = PatientProfile(
                patient_id=patient_id,
                age=45,  # Default provisional age if not supplied
                gender="Not specified",
                consent_for_research=consent_for_research
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)

        # 1. Save original unmodified file to storage (Rule 9: Preserve original data)
        file_ext = Path(original_filename).suffix.lower()
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        saved_file_path = UPLOAD_RAW_DIR / unique_filename

        with open(saved_file_path, "wb") as f:
            f.write(file_bytes)

        # Validate category
        is_valid, err, category = cls.validate_file(original_filename, len(file_bytes))
        if not is_valid:
            raise ValueError(err)

        # 2. Extract or synthesize physiological signal data for preprocessing
        if category == "numerical" and original_filename.endswith(".csv"):
            try:
                # Attempt to parse CSV numbers
                content = file_bytes.decode('utf-8', errors='ignore')
                lines = [line.strip() for line in content.splitlines() if line.strip()]
                signal_vals = []
                for line in lines[:5000]:
                    parts = line.split(',')
                    try:
                        signal_vals.append(float(parts[-1]))
                    except ValueError:
                        continue
                if len(signal_vals) > 100:
                    raw_signal = np.array(signal_vals)
                else:
                    raw_signal = generate_realistic_ecg(duration_seconds=10.0, sampling_rate=sampling_rate)
            except Exception:
                raw_signal = generate_realistic_ecg(duration_seconds=10.0, sampling_rate=sampling_rate)
        elif category == "image":
            # Image format: inspect image file
            image_metadata = ECGImageExtractor.inspect_ecg_image(str(saved_file_path))
            # Generate calibrated reference signal for demonstration while digitizer is staged
            raw_signal = generate_realistic_ecg(duration_seconds=10.0, sampling_rate=sampling_rate)
        else:
            # XML / DICOM / Standard sample
            raw_signal = generate_realistic_ecg(duration_seconds=10.0, sampling_rate=sampling_rate)

        # 3. Execute Preprocessing Pipeline
        pipeline = ECGPreprocessingPipeline(sampling_rate=sampling_rate)
        preprocessing_results = pipeline.process_signal(raw_signal)

        # 4. Execute AI Model Service (Demo / Placeholder)
        patient_metadata = {"patient_id": patient_id, "age": patient.age, "gender": patient.gender}
        ai_inference = ai_service.run_inference(
            raw_signal, 
            sampling_rate=sampling_rate, 
            patient_metadata=patient_metadata
        )

        # 5. Persist ECG Record
        record = ECGRecord(
            patient_id=patient_id,
            original_filename=original_filename,
            stored_filename=unique_filename,
            file_type=category,
            file_path=str(saved_file_path),
            file_size_bytes=len(file_bytes),
            is_public_session=is_public_session,
            session_token=session_token,
            consent_for_research=consent_for_research,
            upload_timestamp=datetime.datetime.utcnow()
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # 6. Persist Analysis Result
        sq = preprocessing_results["signal_quality"]
        cm = preprocessing_results["cardiac_metrics"]
        wv = preprocessing_results["waveform_preview"]

        # If heart rate is significantly abnormal, adapt demo observation
        hr = cm.get("estimated_hr_bpm")
        prediction_label = ai_inference.get("prediction_label", "Normal Sinus Rhythm (Demonstration Reference)")
        if hr:
            if hr > 100:
                prediction_label = "Sinus Tachycardia (Demonstration Reference)"
            elif hr < 60:
                prediction_label = "Sinus Bradycardia (Demonstration Reference)"

        analysis = AnalysisResult(
            ecg_record_id=record.id,
            patient_id=patient_id,
            status=ai_inference.get("status", "completed_demo"),
            is_simulated_demo=True,
            model_name=ai_inference.get("model_name", "DRISTHI Research Prototype"),
            model_version=ai_inference.get("model_version", "0.1.0-alpha"),
            signal_quality_score=sq.get("quality_score"),
            noise_level=sq.get("noise_level"),
            baseline_wander_detected=sq.get("baseline_wander_detected"),
            sampling_rate_hz=sampling_rate,
            duration_seconds=sq.get("duration_seconds"),
            r_peaks_detected_count=cm.get("r_peak_count"),
            estimated_heart_rate_bpm=hr,
            prediction_label=prediction_label,
            confidence_score=ai_inference.get("confidence_score", 0.92),
            classification_categories_json=json.dumps(ai_inference.get("supported_categories", [])),
            observations_json=json.dumps(sq.get("observations", []) + ai_inference.get("observations", [])),
            original_signal_json=json.dumps(wv.get("original_signal", [])),
            processed_signal_json=json.dumps(wv.get("processed_signal", [])),
            created_at=datetime.datetime.utcnow()
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return {
            "record_id": record.id,
            "patient_id": patient_id,
            "filename": original_filename,
            "file_type": category,
            "analysis_id": analysis.id,
            "status": analysis.status,
            "is_simulated_demo": analysis.is_simulated_demo,
            "preprocessing": preprocessing_results,
            "ai_inference": ai_inference
        }

    @classmethod
    def get_analysis_detail(cls, db: Session, analysis_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves complete analysis with waveform signals for visual rendering."""
        analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
        if not analysis:
            return None

        record = db.query(ECGRecord).filter(ECGRecord.id == analysis.ecg_record_id).first()
        
        # Parse waveform data
        orig = json.loads(analysis.original_signal_json) if analysis.original_signal_json else []
        proc = json.loads(analysis.processed_signal_json) if analysis.processed_signal_json else []
        cats = json.loads(analysis.classification_categories_json) if analysis.classification_categories_json else []
        obs = json.loads(analysis.observations_json) if analysis.observations_json else []

        n_pts = len(orig)
        sr = analysis.sampling_rate_hz or 250.0
        time_sec = [round(i / sr, 4) for i in range(n_pts)]

        return {
            "id": analysis.id,
            "ecg_record_id": analysis.ecg_record_id,
            "patient_id": analysis.patient_id,
            "status": analysis.status,
            "is_simulated_demo": analysis.is_simulated_demo,
            "created_at": analysis.created_at.isoformat(),
            "file_details": {
                "original_filename": record.original_filename if record else "ECG Record",
                "file_type": record.file_type if record else "Signal",
                "file_size_bytes": record.file_size_bytes if record else 0,
                "upload_timestamp": record.upload_timestamp.isoformat() if record else ""
            },
            "signal_quality": {
                "quality_score": analysis.signal_quality_score,
                "noise_level": analysis.noise_level,
                "baseline_wander_detected": analysis.baseline_wander_detected,
                "sampling_rate_hz": sr,
                "duration_seconds": analysis.duration_seconds,
                "r_peaks_detected": analysis.r_peaks_detected_count,
                "estimated_heart_rate_bpm": analysis.estimated_heart_rate_bpm
            },
            "prediction": {
                "model_name": analysis.model_name,
                "model_version": analysis.model_version,
                "prediction_label": analysis.prediction_label,
                "confidence_score": analysis.confidence_score,
                "supported_categories": cats,
                "observations": obs,
                "research_disclaimer": (
                    "DRISTHI AI-Assisted Architecture Notice: This model output is currently running in "
                    "Research Demonstration Mode while algorithm benchmarking (IEEE literature / PhysioNet / PTB-XL) "
                    "is underway. Outputs are simulated demonstration data and must not be used for diagnostic or clinical decisions."
                )
            },
            "waveform": {
                "lead_name": "Lead II (Standard Rhythm Strip)",
                "sampling_rate_hz": sr,
                "original_signal": orig,
                "processed_signal": proc,
                "time_seconds": time_sec
            }
        }
