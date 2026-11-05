# DRISTHI REST API Specification

The DRISTHI backend is powered by FastAPI, exposing OpenAPI 3.0 documentation at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

All endpoints are prefixed with `/api/v1`.

---

## 1. Authentication Endpoints (`/api/v1/auth`)

### `POST /auth/register`
Creates a new patient or caregiver account.
* **Payload:**
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "role": "patient", // or "caregiver"
    "full_name": "Jane Doe",
    "patient_id": "PT-1001"
  }
  ```
* **Response:**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "role": "patient",
      "patient_id": "PT-1001"
    }
  }
  ```

### `POST /auth/login`
Authenticates a registered patient or caregiver.
* **Payload:**
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }
  ```

### `GET /auth/me`
Returns the currently authenticated user's profile based on the `Authorization: Bearer <token>` header.

---

## 2. Patient Profile Endpoints (`/api/v1/patients`)

### `GET /patients/{patient_id}`
Retrieves demographic and baseline data for a given Patient ID.

### `POST /patients`
Creates or updates a patient profile.
* **Payload:**
  ```json
  {
    "patient_id": "PT-1001",
    "age": 52,
    "gender": "Male",
    "medical_history": "Hypertension treated with ACE inhibitors",
    "existing_condition": "Paroxysmal Atrial Fibrillation",
    "consent_for_research": true
  }
  ```

### `GET /patients/{patient_id}/records`
Returns all uploaded ECG records, signal quality metrics, and analysis summaries for the patient.

---

## 3. ECG Upload & Processing Endpoints (`/api/v1/ecg`)

### `POST /ecg/upload`
Uploads an ECG file (Image, XML, DICOM, or Numerical CSV).
* **Content-Type:** `multipart/form-data`
* **Form Fields:**
  * `file`: Binary file upload
  * `patient_id`: String (e.g. `PT-1001`)
  * `consent_for_research`: Boolean
  * `sampling_rate`: Float (e.g. `250.0`)
* **Response:**
  ```json
  {
    "success": true,
    "message": "ECG file uploaded and processed successfully.",
    "data": {
      "record_id": 1,
      "patient_id": "PT-1001",
      "analysis_id": 1,
      "status": "completed_demo",
      "is_simulated_demo": true
    }
  }
  ```

### `POST /ecg/sample`
Generates a calibrated 10-second Lead II physiological ECG rhythm for instant pipeline testing.
* **Form Fields:**
  * `patient_id`: String (default: `PT-DEMO-01`)
  * `rhythm_type`: `normal` (72 BPM), `tachycardia` (115 BPM), or `bradycardia` (50 BPM)

---

## 4. Analysis Results Endpoints (`/api/v1/analysis`)

### `GET /analysis/status`
Returns the AI integration subsystem status, benchmark dataset candidates, and target classes.

### `GET /analysis/{analysis_id}`
Retrieves the comprehensive analysis report, including:
* File provenance and storage metadata
* Signal quality score (0.0 to 1.0) and noise classification
* Detected QRS complexes and calculated heart rate (BPM)
* Demonstration prediction and research disclaimer
* Waveform arrays (`original_signal`, `processed_signal`, `r_peak_indices`) for UI visualization.

---

## 5. Caregiver Endpoints (`/api/v1/caregivers`)

### `GET /caregivers/dashboard`
Returns assigned patient vitals summary, recent alerts, and hardware telemetry status.

### `POST /caregivers/alerts/{alert_id}/acknowledge`
Acknowledges an alert advisory.
* **Payload:**
  ```json
  {
    "caregiver_name": "Sarah Jenkins"
  }
  ```

---

## 6. Hardware Monitoring & Telemetry Staging (`/api/v1/monitoring`)

### `GET /monitoring/status`
Reports ESP32 and AD8232 telemetry staging status.

### `POST /monitoring/telemetry`
Staged ingestion endpoint for ESP32 Wi-Fi firmware packets.
* **Payload:**
  ```json
  {
    "device_id": "ESP32-NODE-01",
    "patient_id": "PT-1001",
    "sampling_rate_hz": 250.0,
    "lead_status": "LEAD_ON",
    "voltage_samples": [0.05, 0.08, 0.12, 1.25, -0.20, 0.35]
  }
  ```

