# DRISTHI System Architecture Documentation

**Title:** AI-Assisted ECG Analysis and Patient-Specific Cardiac Monitoring  
**Tagline:** *From ECG Signals to Timely Action.*

---

## 1. Architectural Philosophy

DRISTHI is built on a clean, decoupled modular architecture designed to support iterative scientific research, formal algorithm benchmarking, and eventual microcontroller telemetry integration without requiring architectural rewrites.

```
+-------------------------------------------------------------------------+
|                                CLIENT LAYER                             |
|    React.js + Responsive HealthTech Dashboard (Vite / Vanilla CSS)      |
|  - Public Workflow (No registration required)                           |
|  - Patient Portal (History, Profile, Consent)                           |
|  - Caregiver Dashboard (Advisory feed, Alert ACK, Telemetry status)     |
+------------------------------------+------------------------------------+
                                     | REST APIs (JSON / Multipart)
                                     v
+-------------------------------------------------------------------------+
|                                BACKEND API                              |
|                          FastAPI (Python 3.13+)                         |
|  - Role-aware Auth (Patient / Caregiver; Doctor login excluded)         |
|  - Patient Profile Manager (Strict minimal clinical fields)             |
|  - Non-destructive Upload Handler (Preserves raw original signals)      |
+------------------------------------+------------------------------------+
                                     |
         +---------------------------+---------------------------+
         |                                                       |
         v                                                       v
+----------------------------------+   +----------------------------------+
|      PREPROCESSING PIPELINE      |   |        AI STAGING ADAPTER        |
|  - Zero-phase detrending         |   |  - Abstract Base Class Contract  |
|  - 50Hz mains notch filter       |   |  - Simulated Demo Pipeline       |
|  - 40Hz EMG low-pass filter      |   |  - PTB-XL / MIT-BIH Benchmarking |
|  - Signal Quality Index (SNR)    |   |  - No fabricated clinical claims |
|  - Pan-Tompkins QRS R-peak det.  |   +----------------------------------+
+----------------------------------+
         |                                                       |
         +---------------------------+---------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                                STORAGE                                  |
|  - SQLite (Production-ready via SQLAlchemy ORM for zero-config run)     |
|  - /data/raw: Untouched original file preservation (Rule #9)            |
|  - /data/processed: Conditioned rhythm strips and feature tensors       |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                    FUTURE TELEMETRY / HARDWARE HOOKS                    |
|  - Analog Front End: Analog Devices AD8232 Single-Lead Heart Rate Monitor|
|  - Microcontroller: ESP32 Wi-Fi / BLE Dual-Core 12-bit ADC              |
|  - Protocol: /api/v1/monitoring/telemetry (Staged endpoint)             |
+-------------------------------------------------------------------------+
```

---

## 2. Core Modules Implementation Summary

### Module 1: User Authentication & Access Management
* **Public User:** Immediate access to upload and analysis workflows with temporary session state.
* **Registered Patient:** Email/password authentication, persistent history, personal profile, and research consent controls.
* **Caregiver:** Distinct login role, associated with assigned patients, telemetry advisory monitoring, and alert acknowledgement.
* **Security Rule:** Doctor login functionality is strictly excluded in this release.

### Module 2: Patient Profile
* **Required Fields:** `patient_id` (record key), `age` (physiological rate reference).
* **Optional Fields:** `gender`, `medical_history`, `existing_condition`.
* **Clinical Principle:** Demographic details are never treated as a substitute for objective ECG evidence.

### Module 3: ECG Upload & Input Management
* **Formats Supported:** Images/Photographs (`.png`, `.jpg`), XML (`.xml`), DICOM (`.dcm`), and Numerical Time-Series (`.csv`, `.json`).
* **Validation:** File size limit (25 MB), format extension verification.
* **Integrity Guarantee:** Raw file bytes are permanently preserved in `/data/raw` before any filtering is performed.

### Module 4: ECG Preprocessing Pipeline
* Non-destructive, configurable digital filtering:
  * 0.67 Hz zero-phase high-pass filter (baseline wander suppression).
  * 50 Hz IIR notch filter (powerline hum suppression).
  * 40 Hz low-pass filter (EMG and muscle tremor suppression).
  * Signal Quality Inspector: SNR calculation, noise ratio, flatline/saturation flags.
  * QRS Detector: Pan-Tompkins derivative and energy integration algorithm with 200ms physiological refractory period.
  * Side-by-side visual comparison between original raw and filtered traces.

### Module 5: AI-Based ECG Analysis Integration
* Standardized `BaseECGModel` abstract base class.
* Research demonstration mode clearly labeled with `is_simulated_demo: true`.
* Strict development rule: Zero fabricated diagnoses, zero fake accuracy claims.

### Module 6: Analysis Results Interface
* Comprehensive report surfacing Patient ID, original file metrics, signal quality score, detected R-peaks, calculated heart rate, model demonstration prediction, and medical grid rhythm strip viewer.

### Module 7: Patient Records
* Historical record series per Patient ID.
* Explicit opt-in consent tracking for research dataset participation.

### Module 8: Caregiver Dashboard
* Assigned patient vital signs overview, telemetry staging status, simulated threshold alerts, and alert acknowledgement log.

### Module 9: Hardware Telemetry Staging
* Pre-configured schemas and endpoints for ESP32 and AD8232 analog front-end telemetry streaming (`POST /api/v1/monitoring/telemetry`).
* Clear warnings that live emergency dispatch is not operational.

