import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="patient")  # "patient" or "caregiver"
    full_name = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    patient_profile = relationship("PatientProfile", back_populates="user", uselist=False)
    caregiver_assignments = relationship("CaregiverPatientAssignment", back_populates="caregiver", foreign_keys="CaregiverPatientAssignment.caregiver_id")


class PatientProfile(Base):
    __tablename__ = "patient_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(100), unique=True, index=True, nullable=False)  # Unique identifier for patient
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True)  # Nullable for public/anonymous records
    
    # Core demographic / clinical fields as strictly specified
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=True)
    medical_history = Column(Text, nullable=True)
    existing_condition = Column(Text, nullable=True)
    
    # Consent for research dataset inclusion (strictly opt-in, never automatic)
    consent_for_research = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="patient_profile")
    ecg_records = relationship("ECGRecord", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("PatientAlert", back_populates="patient", cascade="all, delete-orphan")


class CaregiverPatientAssignment(Base):
    __tablename__ = "caregiver_patient_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    caregiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(String(100), ForeignKey("patient_profiles.patient_id"), nullable=False)
    relationship_to_patient = Column(String(100), default="Primary Caregiver")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    caregiver = relationship("User", back_populates="caregiver_assignments")
    patient = relationship("PatientProfile")


class ECGRecord(Base):
    __tablename__ = "ecg_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(100), ForeignKey("patient_profiles.patient_id"), nullable=False, index=True)
    
    # File details
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # "image", "xml", "dicom", "csv", "raw"
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    
    # Access and session boundary
    is_public_session = Column(Boolean, default=False)  # True if uploaded without registered login
    session_token = Column(String(100), nullable=True, index=True)  # For temporary public access
    consent_for_research = Column(Boolean, default=False)  # Never automatically enrolled
    
    upload_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    patient = relationship("PatientProfile", back_populates="ecg_records")
    analysis = relationship("AnalysisResult", back_populates="ecg_record", uselist=False, cascade="all, delete-orphan")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    ecg_record_id = Column(Integer, ForeignKey("ecg_records.id"), nullable=False, unique=True)
    patient_id = Column(String(100), nullable=False, index=True)
    
    # Status & Architecture distinction
    # "awaiting_model" | "completed_demo" | "completed_research" | "error"
    status = Column(String(50), nullable=False, default="awaiting_model")
    is_simulated_demo = Column(Boolean, default=True)  # Strictly labeled per specification
    model_name = Column(String(100), default="DRISTHI Research Prototype (Pending Algorithm Selection)")
    model_version = Column(String(50), default="0.1.0-alpha")
    
    # Preprocessing inspection outputs
    signal_quality_score = Column(Float, nullable=True)  # e.g., 0.0 to 1.0 or SNR dB
    noise_level = Column(String(50), nullable=True)  # "Low", "Moderate", "High"
    baseline_wander_detected = Column(Boolean, default=False)
    sampling_rate_hz = Column(Float, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    r_peaks_detected_count = Column(Integer, nullable=True)
    estimated_heart_rate_bpm = Column(Float, nullable=True)
    
    # Structured Model Predictions (Research placeholders or demo outputs)
    prediction_label = Column(String(100), nullable=True)
    confidence_score = Column(Float, nullable=True)
    classification_categories_json = Column(Text, nullable=True)  # JSON list
    observations_json = Column(Text, nullable=True)  # JSON list of clinical/signal notes
    
    # Waveform signals for UI comparison (original vs preprocessed sample points)
    original_signal_json = Column(Text, nullable=True)
    processed_signal_json = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    ecg_record = relationship("ECGRecord", back_populates="analysis")


class PatientAlert(Base):
    __tablename__ = "patient_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(100), ForeignKey("patient_profiles.patient_id"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    severity = Column(String(50), nullable=False, default="warning")  # "info", "warning", "critical"
    message = Column(Text, nullable=False)
    is_hardware_simulation = Column(Boolean, default=True)  # Marked as simulated until ESP32 live
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    patient = relationship("PatientProfile", back_populates="alerts")
