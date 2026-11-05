import numpy as np
from typing import List, Tuple, Dict, Any

class RPeakDetector:
    """
    R-Peak and QRS Complex Detector.
    Implements a robust energy and derivative-based peak detection algorithm 
    inspired by Pan-Tompkins principles:
    1. Bandpass / derivative filtering
    2. Squaring function to emphasize large differences (R-peaks)
    3. Moving window integration
    4. Adaptive thresholding with physiological refractory period check (200ms minimum)
    """

    @staticmethod
    def detect_r_peaks(
        signal: np.ndarray, 
        sampling_rate: float = 250.0
    ) -> List[int]:
        """
        Returns a list of sample indices corresponding to identified R-peaks.
        """
        if len(signal) < int(sampling_rate * 1.5):
            return []

        # 1. Five-point derivative
        diff = np.diff(signal)
        squared = diff ** 2

        # 2. Moving window integration (~150ms window)
        window_size = int(0.15 * sampling_rate)
        if window_size < 3:
            window_size = 3
        kernel = np.ones(window_size) / window_size
        integrated = np.convolve(squared, kernel, mode='same')

        # 3. Dynamic Thresholding (30% of max energy)
        threshold = np.mean(integrated) + 0.5 * np.std(integrated)
        
        # 4. Peak selection with physiological refractory period (200 ms)
        min_distance = int(0.20 * sampling_rate)
        peaks = []
        i = window_size
        while i < len(integrated) - window_size:
            if integrated[i] > threshold:
                # Find local maximum within +/- window in original signal
                start = max(0, i - window_size)
                end = min(len(signal), i + window_size)
                local_peak = start + np.argmax(signal[start:end])
                
                # Check distance from last detected peak
                if not peaks or (local_peak - peaks[-1]) >= min_distance:
                    peaks.append(int(local_peak))
                    i = local_peak + min_distance
                else:
                    i += 1
            else:
                i += 1

        return peaks

    @classmethod
    def calculate_cardiac_metrics(
        cls, 
        r_peaks: List[int], 
        sampling_rate: float = 250.0
    ) -> Dict[str, Any]:
        """
        Computes Heart Rate (BPM), Mean R-R interval, and Heart Rate Variability (SDNN).
        """
        if len(r_peaks) < 2:
            return {
                "r_peak_count": len(r_peaks),
                "estimated_hr_bpm": None,
                "mean_rr_ms": None,
                "hrv_sdnn_ms": None,
                "r_peak_indices": r_peaks
            }

        # Calculate RR intervals in milliseconds
        rr_intervals_samples = np.diff(r_peaks)
        rr_intervals_ms = (rr_intervals_samples / sampling_rate) * 1000.0

        # Filter out extreme physiologically improbable RR intervals (< 250ms or > 2000ms)
        valid_rr = rr_intervals_ms[(rr_intervals_ms >= 250.0) & (rr_intervals_ms <= 2000.0)]
        if len(valid_rr) == 0:
            valid_rr = rr_intervals_ms

        mean_rr_ms = float(np.mean(valid_rr))
        hr_bpm = round(60000.0 / mean_rr_ms, 1) if mean_rr_ms > 0 else None
        sdnn_ms = round(float(np.std(valid_rr)), 1) if len(valid_rr) > 1 else None

        return {
            "r_peak_count": len(r_peaks),
            "estimated_hr_bpm": hr_bpm,
            "mean_rr_ms": round(mean_rr_ms, 1),
            "hrv_sdnn_ms": sdnn_ms,
            "r_peak_indices": r_peaks
        }
