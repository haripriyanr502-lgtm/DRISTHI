from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# User & Auth Schemas
class UserRole(str):
    PATIENT = "patient"
    CAREGIVER = "caregiver"

class UserRegisterRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", description="Valid email address")
    password: str = Field(..., min_length=6)
    role: str = Field("patient", pattern="^(patient|caregiver)$")
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    patient_id: Optional[str] = None  # If registering as patient or linking to patient

class UserLoginRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    patient_id: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Patient Profile Schemas
class PatientProfileCreate(BaseModel):
    patient_id: str = Field(..., min_length=2, max_length=50, description="Unique Patient Identifier (e.g., PT-001)")
    age: int = Field(..., ge=1, le=125, description="Patient age in years")
    gender: Optional[str] = Field(None, description="Gender (Optional)")
    medical_history: Optional[str] = Field(None, description="Relevant Medical History (Optional)")
    existing_condition: Optional[str] = Field(None, description="Existing Cardiac Condition, if any (Optional)")
    consent_for_research: Optional[bool] = Field(False, description="Explicit opt-in consent for anonymous research study")

class PatientProfileUpdate(BaseModel):
    age: Optional[int] = Field(None, ge=1, le=125)
    gender: Optional[str] = None
    medical_history: Optional[str] = None
    existing_condition: Optional[str] = None
    consent_for_research: Optional[bool] = None

class PatientProfileResponse(BaseModel):
    id: int
    patient_id: str
    age: int
    gender: Optional[str] = None
    medical_history: Optional[str] = None
    existing_condition: Optional[str] = None
    consent_for_research: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ECG Record Schemas
class ECGRecordResponse(BaseModel):
    id: int
    patient_id: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    is_public_session: bool
    consent_for_research: bool
    upload_timestamp: datetime
    has_analysis: bool = False

    class Config:
        from_attributes = True

# Signal Inspection & Quality
class SignalQualityInfo(BaseModel):
    quality_score: float = Field(..., description="Calculated signal SNR / quality index (0.0 to 1.0)")
    noise_level: str = Field(..., description="Assessed noise level: Low, Moderate, High")
    baseline_wander_detected: bool = Field(..., description="Whether low-frequency baseline drift was detected")
    sampling_rate_hz: float = Field(..., description="Estimated or documented sampling rate")
    duration_seconds: float = Field(..., description="Duration of the uploaded ECG segment")
    r_peaks_detected: int = Field(..., description="Detected R-peaks in segment")
    estimated_heart_rate_bpm: Optional[float] = Field(None, description="Calculated beats per minute from R-R intervals")

# Waveform Data for Visualization (Preserves original + processed)
class WaveformSeries(BaseModel):
    lead_name: str = "Lead II (Standard Rhythm Strip)"
    sampling_rate_hz: float = 250.0
    original_signal: List[float]
    processed_signal: List[float]
    r_peak_indices: List[int] = []
    time_seconds: List[float]

# AI Prediction Schema (Structured & clearly marked as research/demo)
class ModelPredictionResult(BaseModel):
    model_name: str
    model_version: str
    status: str  # "completed_demo" | "pending_model_integration"
    is_simulated_demo: bool
    prediction_label: Optional[str] = None
    confidence_score: Optional[float] = None
    supported_categories: List[str] = [
        "Normal Sinus Rhythm",
        "Atrial Fibrillation",
        "Premature Ventricular Contractions (PVC)",
        "Ventricular Bigeminy/Trigeminy",
        "Sinus Bradycardia",
        "Sinus Tachycardia"
    ]
    observations: List[str] = []
    research_disclaimer: str = (
        "DRISTHI AI-Assisted Architecture Notice: This model interface is currently running in "
        "Research Demonstration Mode while algorithm benchmarking (IEEE literature / PhysioNet / PTB-XL) "
        "is underway. Outputs are simulated demonstration data and must not be used for diagnostic or clinical decisions."
    )

class AnalysisResultResponse(BaseModel):
    id: int
    ecg_record_id: int
    patient_id: str
    status: str
    is_simulated_demo: bool
    signal_quality: SignalQualityInfo
    prediction: ModelPredictionResult
    waveform: Optional[WaveformSeries] = None
    created_at: datetime

# Alert Schemas
class AlertResponse(BaseModel):
    id: int
    patient_id: str
    title: str
    severity: str
    message: str
    is_hardware_simulation: bool
    is_acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AlertAcknowledgeRequest(BaseModel):
    caregiver_name: Optional[str] = "Caregiver"

# Caregiver Dashboard Response
class CaregiverDashboardResponse(BaseModel):
    caregiver_name: str
    assigned_patients: List[PatientProfileResponse]
    active_alerts: List[AlertResponse]
    hardware_status_notice: str = (
        "Patient-Specific Hardware Monitoring: ESP32 + AD8232 ECG live stream interface is staged. "
        "Real-time telemetry displays below reflect simulated test feeds awaiting final telemetry link."
    )
