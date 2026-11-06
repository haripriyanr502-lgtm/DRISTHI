
import csv
import io
import json
import math
import uuid
import datetime

from pathlib import Path
from typing import Optional, Dict, Any, Tuple

import numpy as np
from sqlalchemy.orm import Session

from app.config import settings, UPLOAD_RAW_DIR
from app.models.all_models import (
    ECGRecord,
    AnalysisResult,
    PatientProfile
)
from app.preprocessing.pipeline import ECGPreprocessingPipeline
from app.ai.model_service import ai_service


class ECGService:

    @staticmethod
    def validate_file(
        filename: str,
        file_size: int
    ) -> Tuple[bool, str, str]:

        if file_size <= 0:
            return False, "Uploaded file is empty.", ""

        if file_size > settings.MAX_FILE_SIZE_BYTES:
            return False, "File exceeds the maximum permitted size.", ""

        ext = Path(filename).suffix.lower()

        if ext not in settings.ALLOWED_EXTENSIONS:
            return False, f"Unsupported file format: {ext}", ""

        if ext in [".png", ".jpg", ".jpeg"]:
            category = "image"
        elif ext == ".xml":
            category = "xml"
        elif ext == ".dcm":
            category = "dicom"
        else:
            category = "numerical"

        return True, "", category

    @staticmethod
    def extract_csv_signal(
        file_bytes: bytes,
        sampling_rate: float
    ) -> Tuple[np.ndarray, Dict[str, Any]]:

        if not math.isfinite(sampling_rate) or sampling_rate <= 0:
            raise ValueError("Invalid sampling frequency.")

        try:
            content = file_bytes.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(content))

            if not reader.fieldnames:
                raise ValueError("CSV headers are missing.")

            columns = {
                name.strip().lower().replace(" ", "_"): name
                for name in reader.fieldnames
                if name
            }

            preferred_leads = [
                "lead_ii_mv", "lead_ii", "ii", "mlii",
                "lead_i", "i", "v1", "v2", "v3",
                "v4", "v5", "v6"
            ]

            selected_column = None

            for lead in preferred_leads:
                if lead in columns:
                    selected_column = columns[lead]
                    break

            rows = list(reader)

            if selected_column is None:
                excluded = {
                    "sample_index", "index",
                    "time", "time_sec",
                    "timestamp", "record_id"
                }

                candidates = []

                for column in reader.fieldnames:
                    normalized = (
                        column.strip().lower().replace(" ", "_")
                    )

                    if normalized in excluded:
                        continue

                    try:
                        values = [
                            float(row[column])
                            for row in rows
                        ]

                        if values and all(
                            math.isfinite(value)
                            for value in values
                        ):
                            candidates.append(column)

                    except (ValueError, TypeError, KeyError):
                        continue

                if len(candidates) != 1:
                    raise ValueError(
                        "Unable to identify one ECG lead. "
                        "Provide a clearly named ECG column."
                    )

                selected_column = candidates[0]

            signal_values = []

            for row_number, row in enumerate(rows, start=2):

                value = row.get(selected_column)

                if value is None or not value.strip():
                    raise ValueError(
                        f"Missing signal value at row {row_number}."
                    )

                try:
                    sample = float(value)
                except ValueError:
                    raise ValueError(
                        f"Invalid signal value at row {row_number}."
                    )

                if not math.isfinite(sample):
                    raise ValueError(
                        f"Invalid non-finite value at row {row_number}."
                    )

                signal_values.append(sample)

            if len(signal_values) < 100:
                raise ValueError(
                    "At least 100 ECG samples are required."
                )

            raw_signal = np.asarray(
                signal_values,
                dtype=np.float64
            )

            normalized = (
                selected_column.strip().lower().replace(" ", "_")
            )

            unit = (
                "mV"
                if normalized.endswith("_mv")
                or "millivolt" in normalized
                else "unknown"
            )

            metadata = {
                "extraction_method": "CSV numerical extraction",
                "lead_name": selected_column,
                "sampling_rate_hz": sampling_rate,
                "sampling_rate_source": "API parameter",
                "amplitude_unit": unit,
                "sample_count": len(raw_signal),
                "duration_seconds": len(raw_signal) / sampling_rate,
                "extraction_success": True
            }

            return raw_signal, metadata

        except UnicodeDecodeError:
            raise ValueError("CSV must use UTF-8 encoding.")

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

        # 1. Validate file before storage
        is_valid, error, category = cls.validate_file(
            original_filename,
            len(file_bytes)
        )

        if not is_valid:
            raise ValueError(error)

        # 2. Extract actual numerical signal
        if (
            category == "numerical"
            and Path(original_filename).suffix.lower() == ".csv"
        ):
            raw_signal, extraction_metadata = cls.extract_csv_signal(
                file_bytes,
                sampling_rate
            )
        else:
            raise ValueError(
                f"Actual signal extraction for {category} files "
                "has not been implemented yet. "
                "Please upload a supported CSV ECG file."
            )

        # 3. Find or create patient
        patient = (
            db.query(PatientProfile)
            .filter(PatientProfile.patient_id == patient_id)
            .first()
        )

        if not patient:
            patient = PatientProfile(
                patient_id=patient_id,
                age=45,
                gender="Not specified",
                consent_for_research=consent_for_research
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)

        # 4. Preserve original uploaded file
        UPLOAD_RAW_DIR.mkdir(parents=True, exist_ok=True)

        unique_filename = (
            f"{uuid.uuid4().hex}_{Path(original_filename).name}"
        )

        saved_file_path = UPLOAD_RAW_DIR / unique_filename

        with open(saved_file_path, "wb") as file:
            file.write(file_bytes)

        try:
            # 5. Preprocess extracted signal
            pipeline = ECGPreprocessingPipeline(
                sampling_rate=sampling_rate
            )

            preprocessing_results = pipeline.process_signal(
                raw_signal
            )

            # 6. Run existing AI service
            patient_metadata = {
                "patient_id": patient_id,
                "age": patient.age,
                "gender": patient.gender
            }

            ai_inference = ai_service.run_inference(
                raw_signal,
                sampling_rate=sampling_rate,
                patient_metadata=patient_metadata
            )

            # 7. Create ECG record
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
            db.flush()

            # 8. Prepare analysis
            sq = preprocessing_results["signal_quality"]
            cm = preprocessing_results["cardiac_metrics"]
            wv = preprocessing_results["waveform_preview"]

            hr = cm.get("estimated_hr_bpm")

            prediction_label = ai_inference.get(
                "prediction_label",
                "Research demonstration output"
            )

            analysis = AnalysisResult(
                ecg_record_id=record.id,
                patient_id=patient_id,
                status=ai_inference.get(
                    "status",
                    "completed_demo"
                ),
                is_simulated_demo=True,
                model_name=ai_inference.get(
                    "model_name",
                    "DRISTHI Research Prototype"
                ),
                model_version=ai_inference.get(
                    "model_version",
                    "0.1.0-alpha"
                ),
                signal_quality_score=sq.get("quality_score"),
                noise_level=sq.get("noise_level"),
                baseline_wander_detected=sq.get(
                    "baseline_wander_detected"
                ),
                sampling_rate_hz=sampling_rate,
                duration_seconds=sq.get("duration_seconds"),
                r_peaks_detected_count=cm.get("r_peak_count"),
                estimated_heart_rate_bpm=hr,
                prediction_label=prediction_label,
                confidence_score=ai_inference.get(
                    "confidence_score"
                ),
                classification_categories_json=json.dumps(
                    ai_inference.get("supported_categories", [])
                ),
                observations_json=json.dumps(
                    sq.get("observations", [])
                    + ai_inference.get("observations", [])
                ),
                original_signal_json=json.dumps(
                    wv.get("original_signal", [])
                ),
                processed_signal_json=json.dumps(
                    wv.get("processed_signal", [])
                ),
                created_at=datetime.datetime.utcnow()
            )

            db.add(analysis)
            db.commit()

            db.refresh(record)
            db.refresh(analysis)

        except Exception:
            db.rollback()

            if saved_file_path.exists():
                saved_file_path.unlink()

            raise

        return {
            "record_id": record.id,
            "patient_id": patient_id,
            "filename": original_filename,
            "file_type": category,
            "analysis_id": analysis.id,
            "status": analysis.status,
            "is_simulated_demo": analysis.is_simulated_demo,
            "signal_extraction": extraction_metadata,
            "preprocessing": preprocessing_results,
            "ai_inference": ai_inference
        }

    @classmethod
    def get_analysis_detail(
        cls,
        db: Session,
        analysis_id: int
    ) -> Optional[Dict[str, Any]]:

        analysis = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.id == analysis_id)
            .first()
        )

        if not analysis:
            return None

        record = (
            db.query(ECGRecord)
            .filter(ECGRecord.id == analysis.ecg_record_id)
            .first()
        )

        orig = (
            json.loads(analysis.original_signal_json)
            if analysis.original_signal_json else []
        )

        proc = (
            json.loads(analysis.processed_signal_json)
            if analysis.processed_signal_json else []
        )

        cats = (
            json.loads(analysis.classification_categories_json)
            if analysis.classification_categories_json else []
        )

        obs = (
            json.loads(analysis.observations_json)
            if analysis.observations_json else []
        )

        sr = analysis.sampling_rate_hz or 250.0

        time_sec = [
            round(i / sr, 4)
            for i in range(len(orig))
        ]

        return {
            "id": analysis.id,
            "ecg_record_id": analysis.ecg_record_id,
            "patient_id": analysis.patient_id,
            "status": analysis.status,
            "is_simulated_demo": analysis.is_simulated_demo,
            "created_at": analysis.created_at.isoformat(),
            "file_details": {
                "original_filename": (
                    record.original_filename if record else "ECG Record"
                ),
                "file_type": record.file_type if record else "Signal",
                "file_size_bytes": (
                    record.file_size_bytes if record else 0
                ),
                "upload_timestamp": (
                    record.upload_timestamp.isoformat() if record else ""
                )
            },
            "signal_quality": {
                "quality_score": analysis.signal_quality_score,
                "noise_level": analysis.noise_level,
                "baseline_wander_detected": (
                    analysis.baseline_wander_detected
                ),
                "sampling_rate_hz": sr,
                "duration_seconds": analysis.duration_seconds,
                "r_peaks_detected": (
                    analysis.r_peaks_detected_count
                ),
                "estimated_heart_rate_bpm": (
                    analysis.estimated_heart_rate_bpm
                )
            },
            "prediction": {
                "model_name": analysis.model_name,
                "model_version": analysis.model_version,
                "prediction_label": analysis.prediction_label,
                "confidence_score": analysis.confidence_score,
                "supported_categories": cats,
                "observations": obs,
                "research_disclaimer": (
                    "Research demonstration output. "
                    "Not intended for clinical diagnosis."
                )
            },
            "waveform": {
                "sampling_rate_hz": sr,
                "original_signal": orig,
                "processed_signal": proc,
                "time_seconds": time_sec
            }
        }
