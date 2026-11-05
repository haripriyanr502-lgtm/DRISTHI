import math
import random
from typing import List, Dict, Any

DEMO_DATA_DISCLAIMER = "DEMO DATA – NOT A REAL PATIENT RECORD"
MOCK_RESULT_DISCLAIMER = (
    "DEMO DATA – NOT A REAL PATIENT RECORD. "
    "Mock analysis results used strictly to demonstrate the report interface and application workflow. "
    "Not an actual AI prediction, medical diagnosis, or validated accuracy."
)

def generate_synthetic_waveform(
    rhythm_type: str = "normal",
    duration_seconds: float = 10.0,
    sampling_rate: float = 250.0
) -> Dict[str, Any]:
    """
    Generates realistic physiological ECG Lead II waveforms for specific cardiac rhythms.
    Returns:
    - original_signal: untouched raw signal (includes natural baseline drift / noise)
    - processed_signal: conditioned signal (zero-phase baseline drift removed)
    - r_peak_indices: indices of detected QRS complexes
    - time_seconds: timeline array
    """
    num_samples = int(duration_seconds * sampling_rate)
    t = [i / sampling_rate for i in range(num_samples)]
    raw_signal = [0.0] * num_samples
    clean_signal = [0.0] * num_samples
    r_peaks = []

    # Configure heart rate and rhythm properties based on case
    if rhythm_type == "tachycardia":
        base_hr = 116.0
        baseline_drift_amp = 0.22
        noise_amp = 0.05
    elif rhythm_type == "bradycardia":
        base_hr = 52.0
        baseline_drift_amp = 0.12
        noise_amp = 0.03
    elif rhythm_type == "pvc":
        base_hr = 74.0
        baseline_drift_amp = 0.15
        noise_amp = 0.04
    elif rhythm_type == "afib":
        base_hr = 98.0
        baseline_drift_amp = 0.18
        noise_amp = 0.06
    else:  # normal
        base_hr = 72.0
        baseline_drift_amp = 0.14
        noise_amp = 0.03

    # Beat intervals generation
    current_time = 0.15
    beat_times = []
    
    random.seed(42)  # Deterministic seed for reproducible testing
    
    if rhythm_type == "afib":
        # Irregularly irregular RR intervals (classic Atrial Fibrillation)
        while current_time < duration_seconds - 0.2:
            beat_times.append(current_time)
            # Random RR interval varying between 420ms and 850ms
            rr = random.uniform(0.42, 0.85)
            current_time += rr
    elif rhythm_type == "pvc":
        # Mostly regular beats with ectopic PVCs at beats #4 and #8
        beat_idx = 0
        while current_time < duration_seconds - 0.2:
            beat_times.append((current_time, beat_idx in [3, 7]))
            if beat_idx in [2, 6]:
                # Premature beat comes early
                current_time += (60.0 / base_hr) * 0.65
            elif beat_idx in [3, 7]:
                # Compensatory pause after PVC
                current_time += (60.0 / base_hr) * 1.35
            else:
                current_time += 60.0 / base_hr
            beat_idx += 1
    else:
        # Regular sinus pacing
        rr = 60.0 / base_hr
        while current_time < duration_seconds - 0.2:
            beat_times.append(current_time)
            current_time += rr

    # Helper gaussian bell curve for physiological wave segments
    def gaussian(time_val, center_val, width_val, height_val):
        d = time_val - center_val
        return height_val * math.exp(-(d * d) / (2.0 * width_val * width_val))

    # Render beats
    if rhythm_type == "pvc":
        for b_time, is_pvc in beat_times:
            peak_sample = int(b_time * sampling_rate)
            if 0 <= peak_sample < num_samples:
                r_peaks.append(peak_sample)
            
            for i in range(num_samples):
                dt = t[i] - b_time
                if abs(dt) < 0.45:
                    if not is_pvc:
                        # Normal P-Q-R-S-T
                        clean_signal[i] += gaussian(dt, -0.16, 0.035, 0.18)   # P
                        clean_signal[i] += gaussian(dt, -0.04, 0.012, -0.12)  # Q
                        clean_signal[i] += gaussian(dt, 0.0, 0.015, 1.35)     # R
                        clean_signal[i] += gaussian(dt, 0.04, 0.016, -0.28)   # S
                        clean_signal[i] += gaussian(dt, 0.22, 0.065, 0.32)    # T
                    else:
                        # Ectopic PVC: Absent P-wave, Wide bizarre QRS (>120ms), Inverted discordant T-wave
                        clean_signal[i] += gaussian(dt, -0.02, 0.035, 1.45)   # Wide bizarre R
                        clean_signal[i] += gaussian(dt, 0.06, 0.040, -0.65)   # Deep S
                        clean_signal[i] += gaussian(dt, 0.24, 0.080, -0.45)   # Discordant Inverted T
    else:
        for b_time in beat_times:
            peak_sample = int(b_time * sampling_rate)
            if 0 <= peak_sample < num_samples:
                r_peaks.append(peak_sample)

            for i in range(num_samples):
                dt = t[i] - b_time
                if abs(dt) < 0.45:
                    # In AFib, P-wave is absent / replaced by baseline fibrillation
                    if rhythm_type != "afib":
                        clean_signal[i] += gaussian(dt, -0.16, 0.035, 0.18)  # P
                    clean_signal[i] += gaussian(dt, -0.04, 0.012, -0.12)     # Q
                    clean_signal[i] += gaussian(dt, 0.0, 0.015, 1.35)        # R
                    clean_signal[i] += gaussian(dt, 0.04, 0.016, -0.28)      # S
                    clean_signal[i] += gaussian(dt, 0.22, 0.065, 0.32)       # T

    # In AFib: add rapid low-amplitude fibrillatory waves (4-7 Hz)
    afib_f_waves = [0.0] * num_samples
    if rhythm_type == "afib":
        for i in range(num_samples):
            afib_f_waves[i] = 0.08 * math.sin(2 * math.pi * 5.8 * t[i]) + 0.05 * math.sin(2 * math.pi * 7.2 * t[i])
            clean_signal[i] += afib_f_waves[i]

    # Synthesize Raw signal: Clean signal + Realistic Respiratory Baseline Wander + Powerline Hum + Random Noise
    for i in range(num_samples):
        # Respiratory cycle (~0.25 Hz baseline wander)
        wander = baseline_drift_amp * math.sin(2 * math.pi * 0.25 * t[i]) + 0.05 * math.sin(2 * math.pi * 0.1 * t[i])
        # 50 Hz mains hum
        hum = 0.02 * math.sin(2 * math.pi * 50.0 * t[i])
        # Noise
        noise = random.gauss(0, noise_amp)
        raw_signal[i] = round(clean_signal[i] + wander + hum + noise, 4)
        clean_signal[i] = round(clean_signal[i], 4)

    return {
        "original_signal": raw_signal,
        "processed_signal": clean_signal,
        "r_peak_indices": r_peaks,
        "time_seconds": [round(x, 4) for x in t],
        "sampling_rate_hz": sampling_rate,
        "duration_seconds": duration_seconds,
        "calculated_hr_bpm": round(base_hr, 1)
    }

DEMO_CASES: List[Dict[str, Any]] = [
    {
        "case_id": "DEMO-CASE-01",
        "title": "Normal Sinus Rhythm (Standard Baseline)",
        "rhythm_type": "normal",
        "demo_watermark": DEMO_DATA_DISCLAIMER,
        "disclaimer": MOCK_RESULT_DISCLAIMER,
        "patient": {
            "patient_id": "DEMO-PT-001",
            "age": 45,
            "gender": "Male",
            "medical_history": "Annual health checkup. No prior cardiovascular events or active medications.",
            "existing_condition": "None (Healthy Baseline)",
            "consent_for_research": False,
            "is_demo_patient": True
        },
        "recording": {
            "recording_id": "DEMO-REC-001",
            "original_filename": "demo_synthetic_normal_sinus_72bpm.csv",
            "file_type": "numerical",
            "lead_name": "Lead II (Standard Limb Strip)",
            "device": "DRISTHI Synthetic Physiological Generator",
            "sampling_rate_hz": 250.0,
            "duration_seconds": 10.0,
            "calibration": "25 mm/s • 10 mm/mV"
        },
        "mock_analysis": {
            "prediction_label": "Normal Sinus Rhythm (Demo Data)",
            "confidence_score": 0.95,
            "signal_quality_score": 0.96,
            "noise_level": "Low",
            "baseline_wander_detected": False,
            "heart_rate_bpm": 72.0,
            "observations": [
                "DEMO DATA – NOT A REAL PATIENT RECORD.",
                "Uniform P-wave morphology preceding every QRS complex (Normal PR interval 160 ms).",
                "Heart rate calculated at 72.0 BPM, within physiological resting envelope (60-100 BPM).",
                "Minimal baseline wander and low high-frequency noise."
            ]
        }
    },
    {
        "case_id": "DEMO-CASE-02",
        "title": "Sinus Tachycardia (Exertional Rate)",
        "rhythm_type": "tachycardia",
        "demo_watermark": DEMO_DATA_DISCLAIMER,
        "disclaimer": MOCK_RESULT_DISCLAIMER,
        "patient": {
            "patient_id": "DEMO-PT-002",
            "age": 28,
            "gender": "Female",
            "medical_history": "Post-exercise palpitation recording following aerobic training. Non-smoker.",
            "existing_condition": "Sinus Tachycardia (Physiological Exertion)",
            "consent_for_research": False,
            "is_demo_patient": True
        },
        "recording": {
            "recording_id": "DEMO-REC-002",
            "original_filename": "demo_synthetic_tachycardia_116bpm.csv",
            "file_type": "numerical",
            "lead_name": "Lead II (Standard Limb Strip)",
            "device": "DRISTHI Synthetic Physiological Generator",
            "sampling_rate_hz": 250.0,
            "duration_seconds": 10.0,
            "calibration": "25 mm/s • 10 mm/mV"
        },
        "mock_analysis": {
            "prediction_label": "Sinus Tachycardia (Demo Data)",
            "confidence_score": 0.92,
            "signal_quality_score": 0.84,
            "noise_level": "Moderate",
            "baseline_wander_detected": True,
            "heart_rate_bpm": 116.0,
            "observations": [
                "DEMO DATA – NOT A REAL PATIENT RECORD.",
                "Elevated ventricular rate at 116.0 BPM (> 100 BPM resting threshold).",
                "Respiratory motion baseline wander detected and conditioned with zero-phase 0.67 Hz digital filter.",
                "Narrow QRS complex duration (< 90 ms) indicative of supraventricular pacing."
            ]
        }
    },
    {
        "case_id": "DEMO-CASE-03",
        "title": "Sinus Bradycardia (Resting Athletic Rate)",
        "rhythm_type": "bradycardia",
        "demo_watermark": DEMO_DATA_DISCLAIMER,
        "disclaimer": MOCK_RESULT_DISCLAIMER,
        "patient": {
            "patient_id": "DEMO-PT-003",
            "age": 62,
            "gender": "Male",
            "medical_history": "Long-distance cyclist. Asymptomatic resting bradycardia.",
            "existing_condition": "Sinus Bradycardia (Physiological / Athletic)",
            "consent_for_research": False,
            "is_demo_patient": True
        },
        "recording": {
            "recording_id": "DEMO-REC-003",
            "original_filename": "demo_synthetic_bradycardia_52bpm.csv",
            "file_type": "numerical",
            "lead_name": "Lead II (Standard Limb Strip)",
            "device": "DRISTHI Synthetic Physiological Generator",
            "sampling_rate_hz": 250.0,
            "duration_seconds": 10.0,
            "calibration": "25 mm/s • 10 mm/mV"
        },
        "mock_analysis": {
            "prediction_label": "Sinus Bradycardia (Demo Data)",
            "confidence_score": 0.94,
            "signal_quality_score": 0.95,
            "noise_level": "Low",
            "baseline_wander_detected": False,
            "heart_rate_bpm": 52.0,
            "observations": [
                "DEMO DATA – NOT A REAL PATIENT RECORD.",
                "Ventricular rate at 52.0 BPM (< 60 BPM standard threshold).",
                "Regular rhythm with preserved P-QRS-T relationship and normal QT interval.",
                "Clean rhythm strip with high signal-to-noise ratio."
            ]
        }
    },
    {
        "case_id": "DEMO-CASE-04",
        "title": "Premature Ventricular Contractions (PVC Ectopic Beats)",
        "rhythm_type": "pvc",
        "demo_watermark": DEMO_DATA_DISCLAIMER,
        "disclaimer": MOCK_RESULT_DISCLAIMER,
        "patient": {
            "patient_id": "DEMO-PT-004",
            "age": 55,
            "gender": "Male",
            "medical_history": "Occasional sensation of 'skipped beats' while resting. Controlled hypertension.",
            "existing_condition": "Frequent Premature Ventricular Contractions",
            "consent_for_research": False,
            "is_demo_patient": True
        },
        "recording": {
            "recording_id": "DEMO-REC-004",
            "original_filename": "demo_synthetic_pvc_ectopic_74bpm.csv",
            "file_type": "numerical",
            "lead_name": "Lead II (Standard Limb Strip)",
            "device": "DRISTHI Synthetic Physiological Generator",
            "sampling_rate_hz": 250.0,
            "duration_seconds": 10.0,
            "calibration": "25 mm/s • 10 mm/mV"
        },
        "mock_analysis": {
            "prediction_label": "Premature Ventricular Contractions (Demo Data)",
            "confidence_score": 0.89,
            "signal_quality_score": 0.88,
            "noise_level": "Low",
            "baseline_wander_detected": False,
            "heart_rate_bpm": 74.0,
            "observations": [
                "DEMO DATA – NOT A REAL PATIENT RECORD.",
                "Isolated premature ectopic QRS complexes observed with wide morphology (> 120 ms).",
                "Compensatory pauses noted immediately following ectopic beats.",
                "Background underlying rhythm remains regular sinus pacing at ~74 BPM."
            ]
        }
    },
    {
        "case_id": "DEMO-CASE-05",
        "title": "Atrial Fibrillation (Irregularly Irregular R-R Intervals)",
        "rhythm_type": "afib",
        "demo_watermark": DEMO_DATA_DISCLAIMER,
        "disclaimer": MOCK_RESULT_DISCLAIMER,
        "patient": {
            "patient_id": "DEMO-PT-005",
            "age": 68,
            "gender": "Female",
            "medical_history": "History of paroxysmal atrial fibrillation on oral anticoagulant therapy.",
            "existing_condition": "Atrial Fibrillation with Rapid Ventricular Response",
            "consent_for_research": False,
            "is_demo_patient": True
        },
        "recording": {
            "recording_id": "DEMO-REC-005",
            "original_filename": "demo_synthetic_atrial_fibrillation_98bpm.csv",
            "file_type": "numerical",
            "lead_name": "Lead II (Standard Limb Strip)",
            "device": "DRISTHI Synthetic Physiological Generator",
            "sampling_rate_hz": 250.0,
            "duration_seconds": 10.0,
            "calibration": "25 mm/s • 10 mm/mV"
        },
        "mock_analysis": {
            "prediction_label": "Atrial Fibrillation (Demo Data)",
            "confidence_score": 0.91,
            "signal_quality_score": 0.82,
            "noise_level": "Moderate",
            "baseline_wander_detected": True,
            "heart_rate_bpm": 98.0,
            "observations": [
                "DEMO DATA – NOT A REAL PATIENT RECORD.",
                "Complete absence of distinct P-waves with fine fibrillatory baseline activity.",
                "Irregularly irregular R-R intervals with variable ventricular response.",
                "Mean ventricular rate recorded at ~98 BPM over the 10-second window."
            ]
        }
    }
]

def get_demo_case_by_id(case_id: str) -> Dict[str, Any]:
    """Retrieves a demo case along with its freshly generated synthetic waveform data."""
    for c in DEMO_CASES:
        if c["case_id"] == case_id:
            wf = generate_synthetic_waveform(
                rhythm_type=c["rhythm_type"],
                duration_seconds=c["recording"]["duration_seconds"],
                sampling_rate=c["recording"]["sampling_rate_hz"]
            )
            case_data = dict(c)
            case_data["waveform"] = wf
            return case_data
    return None

