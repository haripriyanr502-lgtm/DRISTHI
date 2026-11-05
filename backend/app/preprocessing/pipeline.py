import numpy as np
from typing import Dict, Any, Tuple, Optional
from app.preprocessing.signal_filters import SignalFilterModule
from app.preprocessing.quality_inspector import SignalQualityInspector
from app.preprocessing.r_peak_detector import RPeakDetector
from app.preprocessing.image_extractor import ECGImageExtractor

class ECGPreprocessingPipeline:
    """
    Main ECG Preprocessing Pipeline.
    Strictly follows DRISTHI core requirements:
    1. Preserves the original raw ECG data at all times.
    2. Allows side-by-side comparison of original and conditioned signals.
    3. Modular, configurable transformations (never blindly applied).
    4. Evaluates real quality metrics (noise, baseline wander, QRS detection).
    """

    def __init__(
        self,
        sampling_rate: float = 250.0,
        apply_baseline_removal: bool = True,
        apply_powerline_removal: bool = True,
        apply_noise_filter: bool = True,
        apply_normalization: bool = True,
        normalization_method: str = "z_score"
    ):
        self.sampling_rate = sampling_rate
        self.apply_baseline_removal = apply_baseline_removal
        self.apply_powerline_removal = apply_powerline_removal
        self.apply_noise_filter = apply_noise_filter
        self.apply_normalization = apply_normalization
        self.normalization_method = normalization_method

    def process_signal(
        self, 
        raw_signal: np.ndarray,
        time_vector: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Executes preprocessing steps on numerical ECG data while maintaining
        the raw unmodified signal for visual and research comparison.
        """
        # Ensure numpy 1D array
        raw_array = np.array(raw_signal, dtype=float)
        
        # 1. Quality inspection on the untouched raw signal
        quality_assessment = SignalQualityInspector.inspect(raw_array, self.sampling_rate)

        # 2. Sequential, non-destructive filtering
        processed = raw_array.copy()

        if self.apply_baseline_removal:
            processed = SignalFilterModule.remove_baseline_wander(
                processed, sampling_rate=self.sampling_rate, cutoff_hz=0.67
            )

        if self.apply_powerline_removal:
            processed = SignalFilterModule.remove_powerline_interference(
                processed, sampling_rate=self.sampling_rate, freq_hz=50.0
            )

        if self.apply_noise_filter:
            processed = SignalFilterModule.remove_high_frequency_noise(
                processed, sampling_rate=self.sampling_rate, cutoff_hz=40.0
            )

        # 3. R-Peak detection on conditioned signal
        r_peaks = RPeakDetector.detect_r_peaks(processed, self.sampling_rate)
        cardiac_metrics = RPeakDetector.calculate_cardiac_metrics(r_peaks, self.sampling_rate)

        # 4. Normalization if requested
        display_processed = processed.copy()
        if self.apply_normalization:
            display_processed = SignalFilterModule.normalize_signal(
                display_processed, method=self.normalization_method
            )

        # Generate time vector if not provided
        n_points = len(raw_array)
        if time_vector is None or len(time_vector) != n_points:
            t = np.linspace(0.0, n_points / self.sampling_rate, n_points)
        else:
            t = time_vector

        # Limit sample points for lightweight JSON delivery (first 10 seconds or up to 2500 pts)
        max_preview_pts = min(2500, n_points)
        preview_indices = np.linspace(0, n_points - 1, max_preview_pts, dtype=int)

        return {
            "signal_quality": quality_assessment,
            "cardiac_metrics": cardiac_metrics,
            "pipeline_config": {
                "sampling_rate_hz": self.sampling_rate,
                "baseline_wander_filtered": self.apply_baseline_removal,
                "powerline_notch_applied": self.apply_powerline_removal,
                "noise_filter_applied": self.apply_noise_filter,
                "normalization": self.normalization_method if self.apply_normalization else "none"
            },
            "waveform_preview": {
                "lead_name": "Lead II (Standard Rhythm Strip)",
                "sampling_rate_hz": self.sampling_rate,
                "original_signal": [round(float(x), 4) for x in raw_array[preview_indices]],
                "processed_signal": [round(float(x), 4) for x in display_processed[preview_indices]],
                "r_peak_indices": [int(p) for p in r_peaks if p < max_preview_pts],
                "time_seconds": [round(float(x), 4) for x in t[preview_indices]]
            }
        }
