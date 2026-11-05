# DRISTHI — AI-Assisted ECG Analysis and Patient-Specific Cardiac Monitoring

> **Tagline:** *From ECG Signals to Timely Action.*

DRISTHI is an open, modular HealthTech web platform designed to ingest multi-format electrocardiograms, condition raw signals through scientific preprocessing pipelines, and present understandable cardiac rhythm insights to patients and caregivers.

---

## 1. System Overview & Core Philosophy

DRISTHI is architected with strict adherence to scientific research standards:
1. **Public Accessibility:** Anyone can open the website, upload an ECG, and inspect conditioned signals without mandatory registration.
2. **Data Integrity:** Uploaded raw ECG records are permanently preserved without modification (`/data/raw/`).
3. **No Fabricated Diagnoses:** While parallel machine-learning algorithm benchmarking (IEEE literature, PTB-XL, MIT-BIH) is conducted, all model inferences are transparently labeled as **Research Demonstration Data**.
4. **Caregiver Oversight:** Caregivers have access to assigned patient monitoring feeds, alert acknowledgements, and staged hardware telemetry integration.
5. **Role Boundary:** Doctor login is intentionally excluded from this release.

---

## 2. Technology Stack

* **Frontend:**
  * React.js 19 with Vite 8
  * JavaScript (ES6+), HTML5, CSS3
  * Responsive HealthTech Design System
  * Custom Medical-Grade SVG Rhythm Strip Visualizer with 25mm/s 10mm/mV Grid
  * Lucide React Icons
* **Backend:**
  * Python 3.13+
  * FastAPI (Asynchronous REST API)
  * Uvicorn ASGI Server
  * Pydantic v2 (Input validation & Schemas)
  * PyJWT & Bcrypt (Secure authentication)
* **Database & Storage:**
  * SQLite via SQLAlchemy 2.0 ORM (Zero-configuration local setup, easily swappable for PostgreSQL)
  * File storage for original raw records (`/data/raw/`) and processed waveforms (`/data/processed/`)
* **Signal Processing & Preprocessing:**
  * NumPy (Vectorized signal array manipulation)
  * Pan-Tompkins QRS Energy Detector (R-peak and heart rate computation)
  * Digital Butterworth & Notch Filters (Baseline wander & 50Hz mains suppression)

---

## 3. Project Directory Structure

```
DRISTHI/
│
├── frontend/                     # React + Vite web client
│   ├── src/
│   │   ├── components/           # Navbar, Footer, ECGWaveformViewer, MetricCard, StatusBadge
│   │   ├── context/              # AuthContext (Role-aware session state)
│   │   ├── pages/                # 10 application pages
│   │   ├── services/             # API client (Fetch / Axios wrapper)
│   │   ├── styles/               # index.css (HealthTech color palette & medical grid)
│   │   ├── App.jsx               # Router & state coordinator
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/                      # FastAPI Python REST application
│   ├── app/
│   │   ├── api/                  # API routes (auth, patients, ecg, analysis, caregivers, monitoring, health)
│   │   ├── database/             # SQLAlchemy session and engine
│   │   ├── models/               # SQLAlchemy ORM models (User, Patient, ECGRecord, Analysis, Alert)
│   │   ├── schemas/              # Pydantic v2 schemas
│   │   ├── preprocessing/        # Digital filters, quality inspector, R-peak detector, image extractor
│   │   ├── ai/                   # Abstract base model, model service manager, simulated demo pipeline
│   │   ├── services/             # ECG service, Auth service, Patient service, Notification service
│   │   ├── config.py             # Application settings & environment variables
│   │   └── main.py               # FastAPI application entrypoint
│   ├── requirements.txt          # Python dependencies
│   └── test_backend.py           # End-to-end verification and smoke test suite
│
├── data/
│   ├── raw/                      # Unmodified uploaded ECG files (Rule #9: preserved)
│   ├── processed/                # Conditioned signals and features
│   └── sample/                   # Verified physiological Lead II calibration samples
│
├── docs/
│   ├── architecture.md           # Decoupled system architecture documentation
│   ├── api.md                    # REST API endpoint specifications & curl examples
│   └── research_roadmap.md       # IEEE benchmarking roadmap & ESP32+AD8232 specs
│
├── venv/                         # Python virtual environment
└── README.md                     # Project documentation
```

---

## 4. Local Setup & Installation

### Prerequisites
* **Python:** 3.10 to 3.13 installed
* **Node.js:** v18+ or v22+ with npm

---

### Step 1: Backend Installation & Setup

1. Open PowerShell or Terminal in the root `Dristhi` directory.
2. Activate or create the Python virtual environment:
   ```powershell
   # If venv is not yet created:
   python -m venv venv

   # Activate on Windows:
   .\venv\Scripts\Activate.ps1
   ```
3. Install backend dependencies:
   ```powershell
   pip install -r backend/requirements.txt
   ```
4. Verify backend configuration with the built-in smoke test:
   ```powershell
   python backend/test_backend.py
   ```
   *Expected output: `ALL MODULE VERIFICATION CHECKS PASSED (6/6)!`*

---

### Step 2: Frontend Installation

1. Navigate to the frontend directory:
   ```powershell
   cd frontend
   ```
2. Install Node dependencies:
   ```powershell
   npm install
   ```
3. Verify the production build:
   ```powershell
   npm run build
   ```

---

## 5. Running the Application

### Start the Backend Server (FastAPI)
From the root directory with virtual environment activated:
```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
* The backend will start on: **`http://127.0.0.1:8000`**
* Interactive Swagger API documentation: **`http://127.0.0.1:8000/docs`**
* Alternative ReDoc documentation: **`http://127.0.0.1:8000/redoc`**

### Start the Frontend Server (Vite / React)
From another terminal window:
```powershell
cd frontend
npm run dev
```
* The frontend will start on: **`http://localhost:5173`**

---

## 6. Application Pages & Navigation

| Page | Path / Tab | Access Role | Description |
|---|---|---|---|
| **Home Page** | `home` | Public | Platform overview, 7-stage architecture breakdown, direct CTAs. |
| **Login / Registration** | `auth` | Public | Account creation for Patient or Caregiver (doctor login excluded). |
| **Patient Profile** | `profile` | Patient / Public | Patient ID, Age, Gender, Medical History, Cardiac condition, opt-in consent. |
| **ECG Upload** | `upload` | Public / Patient | Drag-and-drop, format validation, size check, instant sample rhythm loader. |
| **ECG Analysis** | `analysis` | Public / Patient | Digital filter configuration, QRS detection preview, AI architecture specs. |
| **Analysis Results** | `results` | Public / Patient | Side-by-side medical grid waveform comparison, heart rate, signal quality, demo prediction. |
| **Patient Dashboard** | `patient-dashboard`| Patient | Record counts, vitals overview, quick actions, latest uploads table. |
| **Caregiver Dashboard**| `caregiver-dashboard`| Caregiver | Assigned patients list, live advisory feed, alert acknowledgement interface. |
| **Patient ECG History**| `history` | Patient | Comprehensive historical record series, filter by format, view previous reports. |
| **Settings & Diagnostics**| `settings` | All | Session patient ID switcher, backend health check, hardware staging specs. |

---

## 7. HealthTech Color Palette

The user interface adheres to a clean, accessible healthcare theme:
* **Navy (`#12304A`):** Primary branding, page titles, main navigation headers.
* **Blue (`#2878B5`):** Secondary interactive elements, links, informative badges.
* **Teal (`#20A39E`):** Primary action buttons, signal quality highlights, success markers.
* **White (`#FFFFFF`):** High-contrast cards, input surfaces, active tabs.
* **Light Background (`#F3F8FB`):** Soft, eye-friendly clinical workspace background.
* **Light Grey (`#E5EDF3`):** Neutral borders, timeline dividers, secondary buttons.
* **Alert Red (`#D9534F`):** Critical alerts, threshold warnings, raw unconditioned trace overlay.

---

## 8. Completed Features vs. Pending Research Roadmap

### Completed Features (Implemented in this Deliverable)
- [x] Full-stack architecture with decoupled React.js frontend and FastAPI backend.
- [x] Zero-configuration SQLite database via SQLAlchemy 2.0 with modular schema.
- [x] Public user workflow (no registration mandatory to upload, preprocess, and analyze ECGs).
- [x] Registered Patient and Caregiver role-aware authentication (Doctor login excluded).
- [x] Dedicated Patient Profile management (Patient ID, Age, Gender, Medical History, Cardiac condition).
- [x] Multi-format ECG upload support (Images `.png/.jpg`, XML `.xml`, DICOM `.dcm`, Numerical `.csv/.json`).
- [x] File size (<25MB) and extension validation with drag-and-drop and progress bar.
- [x] Permanent preservation of original raw uploaded ECG data in `/data/raw/`.
- [x] Non-destructive digital preprocessing pipeline:
  - 0.67 Hz zero-phase baseline wander suppression.
  - 50 Hz powerline mains notch filtering.
  - 40 Hz EMG noise attenuation.
  - Signal Quality Index (SNR) and noise classification.
  - Pan-Tompkins QRS R-peak detection and physiological Heart Rate (BPM) calculation.
- [x] Interactive SVG rhythm strip viewer with authentic 25mm/s 10mm/mV medical grid, time/voltage axes, zoom/pan controls, and side-by-side original vs. processed overlay.
- [x] Modular AI inference adapter (`BaseECGModel`) with demonstration mode and strict non-fabrication disclaimers.
- [x] Caregiver dashboard with assigned patients, telemetry staging status, and alert acknowledgement.
- [x] Explicit opt-in consent tracking for research dataset participation (Rule #5).
- [x] Dedicated Temporary DEMO DATA Mode with 5 realistic synthetic ECG cases (Normal, Tachycardia, Bradycardia, PVC, Atrial Fibrillation).
- [x] Prominent "DEMO DATA – NOT A REAL PATIENT RECORD" watermark enforcement on all synthetic waveforms, reports, and dashboards.
- [x] Automated test suite (`test_backend.py`) verifying all 6 core sub-modules.

### Pending Research & Future Integration Tasks
- [ ] **Algorithm Benchmarking:** Formal evaluation of 1D-ResNet vs. Bi-LSTM vs. PatchTST on the PTB-XL dataset (21,837 clinical records) and PhysioNet MIT-BIH.
- [ ] **Optical Waveform Digitization:** Implementation of OpenCV / deep contour extraction pipeline for converting photographed ECG paper grid coordinates to mV time-series.
- [ ] **DICOM Waveform Parser:** Extended parsing for 12-lead encapsulated DICOM ECG SOP classes.
- [ ] **Microcontroller Telemetry:** Firmware deployment for ESP32 Wi-Fi streaming from the Analog Devices AD8232 single-lead analog front-end.
- [ ] **Real-time WebSocket Streaming:** Continuous live buffer ingestion and automated arrhythmia threshold notifications.

---

## 9. Regulatory & Medical Disclaimer

> **IMPORTANT:** DRISTHI is an open health technology and engineering research prototype. All predictive insights and classification outputs generated by the initial platform are for demonstration and research purposes only. DRISTHI does not provide medical diagnoses, clinical validation, or emergency cardiac alerting services. Always consult a qualified medical professional for health-related concerns.

