# DRISTHI Research Roadmap & AI Integration Blueprint

This document outlines the parallel scientific research and engineering milestones for DRISTHI's transition from research demonstration to production algorithm deployment.

---

## 1. IEEE Literature & Algorithm Benchmarking

### Candidate Machine Learning Architectures Under Review:
1. **1D Deep Residual Convolutional Neural Networks (1D-ResNet-34 / 1D-ResNet-50):**
   * *Rationale:* Proven gold standard for 12-lead and single-lead ECG rhythm classification. Skip connections prevent vanishing gradients when processing long time-series windows (5,000 samples @ 500 Hz).
   * *Target Paper:* Strodthoff et al., *"Deep Learning for ECG Analysis: Benchmarks and Knowledge Mapping on PTB-XL"*, IEEE Journal of Biomedical and Health Informatics (JBHI).
2. **Bidirectional Long Short-Term Memory with Self-Attention (Bi-LSTM + Attention):**
   * *Rationale:* Captures morphological features inside the QRS complex with forward-backward temporal context, while attention weights highlight abnormal ectopic beats (PVCs, PACs).
3. **Patch Time Series Transformer (PatchTST / Vision Transformer for ECG):**
   * *Rationale:* Segments continuous voltage traces into overlapping sub-beat patches, yielding state-of-the-art rhythm representation transferability.

---

## 2. Benchmark Datasets Under Investigation

| Dataset | Records | Leads | Sampling Rate | Primary Classification Focus |
|---|---|---|---|---|
| **PTB-XL** | 21,837 | 12 | 500 Hz / 100 Hz | Diagnostic statements, Form & Rhythm statements (SCP-ECG) |
| **MIT-BIH Arrhythmia** | 48 (30-min) | 2 | 360 Hz | Beat-by-beat annotation of premature ventricular contractions |
| **Chapman-Shaoxing** | 10,646 | 12 | 500 Hz | 11 rhythm categories and 56 rhythm-conduction phenotypes |

---

## 3. Preprocessing Engineering Principles

* **Zero-Phase Digital Filtering:** Using bidirectional forward-backward filters (`scipy.signal.filtfilt`) ensures zero phase distortion, preserving the exact clinical onset and offset points of the P-wave, Q-wave, and T-wave.
* **Baseline Wander Detrending:** 0.67 Hz cutoff eliminates respiration artifacts without attenuating low-frequency ST-segment changes (critical for ischemia and infarction assessment).
* **Powerline Notch:** Selectable 50 Hz or 60 Hz narrow-band notch (Q-factor = 30) for clinical mains hum attenuation.
* **Image Digitization Modular Separation:** OCR / OpenCV grid line segmentation is strictly decoupled from 1D physiological time-series processing to avoid contaminating numerical signals with optical raster artifacts.

---

## 4. Hardware Integration Roadmap (ESP32 + AD8232)

### Stage 1: Sensor Interfacing & Signal Conditioning
* **Analog Front End (AFE):** Analog Devices **AD8232**.
  * Instrumentation amplifier with gain = 100 V/V.
  * Right Leg Drive (RLD) circuit to invert common-mode noise.
  * Hardware high-pass filter cutoff at 0.5 Hz; low-pass cutoff at 40 Hz.
  * Leads-Off Detection: `LO+` and `LO-` connected to ESP32 digital GPIOs.

### Stage 2: Embedded Digitization (ESP32)
* 12-bit Successive Approximation Register (SAR) ADC.
* Continuous sampling via FreeRTOS timer interrupt at 250 Hz.
* Sliding 2.5-second buffer (625 samples).

### Stage 3: Secure Telemetry Dispatch
* Microcontroller transmits compressed JSON or Protocol Buffers packets over WPA3 Wi-Fi to `/api/v1/monitoring/telemetry`.
* Telemetry packet validation and caregiver threshold alerting.

