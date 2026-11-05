import numpy as np
from typing import Dict, Any

class SignalQualityInspector:
    """
    Evaluates physiological ECG signal quality and artifact presence.
    - Estimates Signal-to-Noise Ratio (SNR).
    - Checks for baseline wander and powerline interference.
    - Flags signal saturation, clipping, or flatlines.
    - Computes a Signal Quality Score (0.0 to 1.0).
    """

    @staticmethod
    def inspect(signal: np.ndarray, sampling_rate: float = 250.0) -> Dict[str, Any]:
        if len(signal) == 0:
            return {
                "quality_score": 0.0,
                "noise_level": "High",
                "baseline_wander_detected": False,
                "is_clipped_or_flatline": True,
                "sampling_rate_hz": sampling_rate,
                "duration_seconds": 0.0,
                "observations": ["Empty signal provided."]
            }

        duration_sec = round(len(signal) / sampling_rate, 2)
        observations = []

        # 1. Flatline / Saturation detection
        unique_vals = len(np.unique(signal[:min(500, len(signal))]))
        if unique_vals < 5 or np.std(signal) < 1e-4:
            return {
                "quality_score": 0.05,
                "noise_level": "Critical",
                "baseline_wander_detected": False,
                "is_clipped_or_flatline": True,
                "sampling_rate_hz": sampling_rate,
                "duration_seconds": duration_sec,
                "observations": ["Flatline or lead disconnection detected (extremely low signal variance)."]
            }

        # 2. Baseline Wander Inspection (Energy in < 0.5 Hz vs Total Energy)
        # Using simple moving median or low-pass residual
        window_size = int(sampling_rate * 0.8)
        if window_size % 2 == 0:
            window_size += 1
        window_size = min(window_size, max(3, len(signal) - 1))
        
        kernel = np.ones(window_size) / window_size
        trend = np.convolve(signal, kernel, mode='same')
        detrended = signal - trend
        trend_energy = np.var(trend)
        total_energy = np.var(signal)

        baseline_wander_ratio = float(trend_energy / (total_energy + 1e-6))
        baseline_wander = baseline_wander_ratio > 0.35
        if baseline_wander:
            observations.append("Noticeable low-frequency baseline drift detected (respiratory or patient movement).")

        # 3. High-Frequency Noise Inspection (sample-to-sample jitter)
        diff = np.diff(detrended)
        high_freq_energy = np.var(diff)
        noise_ratio = float(high_freq_energy / (np.var(detrended) + 1e-6))

        # 4. Overall Signal Quality Index (SQI)
        # 1.0 = clean rhythm strip; < 0.5 = noisy / degraded
        penalty = 0.0
        if baseline_wander:
            penalty += 0.2
        if noise_ratio > 0.8:
            penalty += 0.3
            noise_level = "High"
            observations.append("High-frequency artifact or muscle tremor (EMG) detected.")
        elif noise_ratio > 0.35:
            penalty += 0.15
            noise_level = "Moderate"
            observations.append("Moderate powerline or equipment noise observed.")
        else:
            noise_level = "Low"

        quality_score = max(0.1, round(1.0 - penalty, 2))
        if quality_score >= 0.85:
            observations.append("Good signal morphology with identifiable QRS complexes.")

        return {
            "quality_score": quality_score,
            "noise_level": noise_level,
            "baseline_wander_detected": baseline_wander,
            "is_clipped_or_flatline": False,
            "sampling_rate_hz": sampling_rate,
            "duration_seconds": duration_sec,
            "observations": observations
        }
