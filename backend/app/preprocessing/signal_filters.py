import numpy as np
from typing import Tuple, Optional

try:
    from scipy.signal import butter, filtfilt, iirnotch
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

class SignalFilterModule:
    """
    ECG Signal Filtering & Conditioning.
    Designed according to standard physiological signal processing principles:
    - Zero-phase filtering (filtfilt) to prevent distortion of ECG P-Q-R-S-T morphology.
    - Baseline wander removal (0.5 Hz high-pass or moving median).
    - Powerline interference removal (50/60 Hz notch).
    - High-frequency EMG/muscle artifact suppression (35-45 Hz low-pass).
    - Normalization with preservation of original reference units.
    """

    @staticmethod
    def remove_baseline_wander(
        signal: np.ndarray, 
        sampling_rate: float = 250.0, 
        cutoff_hz: float = 0.67
    ) -> np.ndarray:
        """
        Removes baseline wander caused by patient respiration and body motion.
        Uses a bi-directional Butterworth high-pass filter (zero phase shift).
        """
        if not SCIPY_AVAILABLE or len(signal) < 15:
            # Fallback pure-python moving average detrending if scipy is not yet loaded
            window_size = int(sampling_rate * 0.8)
            if window_size % 2 == 0:
                window_size += 1
            if len(signal) > window_size:
                baseline = np.convolve(signal, np.ones(window_size)/window_size, mode='same')
                return signal - baseline
            return signal - np.mean(signal)

        nyquist = 0.5 * sampling_rate
        norm_cutoff = min(cutoff_hz / nyquist, 0.99)
        b, a = butter(2, norm_cutoff, btype='highpass', analog=False)
        # filtfilt applies filter forwards and backwards for zero phase distortion
        cleaned = filtfilt(b, a, signal)
        return cleaned

    @staticmethod
    def remove_powerline_interference(
        signal: np.ndarray, 
        sampling_rate: float = 250.0, 
        freq_hz: float = 50.0, 
        q_factor: float = 30.0
    ) -> np.ndarray:
        """
        Notch filter to eliminate 50 Hz or 60 Hz electrical mains interference.
        """
        if not SCIPY_AVAILABLE or len(signal) < 15:
            return signal

        nyquist = 0.5 * sampling_rate
        if freq_hz >= nyquist:
            return signal  # Cannot filter frequency above Nyquist limit

        w0 = freq_hz / nyquist
        b, a = iirnotch(w0, q_factor)
        cleaned = filtfilt(b, a, signal)
        return cleaned

    @staticmethod
    def remove_high_frequency_noise(
        signal: np.ndarray, 
        sampling_rate: float = 250.0, 
        cutoff_hz: float = 40.0
    ) -> np.ndarray:
        """
        Low-pass filter to attenuate muscle tremor (EMG) and instrumentation noise.
        """
        if not SCIPY_AVAILABLE or len(signal) < 15:
            return signal

        nyquist = 0.5 * sampling_rate
        norm_cutoff = min(cutoff_hz / nyquist, 0.99)
        b, a = butter(2, norm_cutoff, btype='lowpass', analog=False)
        cleaned = filtfilt(b, a, signal)
        return cleaned

    @staticmethod
    def normalize_signal(signal: np.ndarray, method: str = "z_score") -> np.ndarray:
        """
        Normalizes the amplitude.
        Supports 'z_score' (zero mean, unit variance) or 'min_max' (scaled to [-1, 1]).
        """
        if len(signal) == 0:
            return signal

        if method == "z_score":
            std = np.std(signal)
            if std == 0 or np.isnan(std):
                return signal - np.mean(signal)
            return (signal - np.mean(signal)) / std
        elif method == "min_max":
            min_val = np.min(signal)
            max_val = np.max(signal)
            if max_val == min_val:
                return np.zeros_like(signal)
            return 2.0 * ((signal - min_val) / (max_val - min_val)) - 1.0
        return signal
