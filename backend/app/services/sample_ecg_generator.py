import math
import random
from typing import List, Union, Any

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

def generate_realistic_ecg(
    duration_seconds: float = 10.0,
    sampling_rate: float = 250.0,
    heart_rate_bpm: float = 72.0,
    noise_amplitude: float = 0.04,
    baseline_wander: bool = True
) -> Union[List[float], Any]:
    """
    Generates a realistic Lead-II ECG waveform based on physiological wave parameters:
    P-wave, PR-segment, Q-wave, R-peak, S-wave, ST-segment, T-wave.
    Includes natural baseline wander (respiration ~0.25 Hz) and slight electromyographic noise.
    Works with either NumPy or pure Python.
    """
    num_samples = int(duration_seconds * sampling_rate)
    beat_period = 60.0 / heart_rate_bpm
    
    signal = [0.0] * num_samples
    
    for i in range(num_samples):
        t = i / sampling_rate
        phase = (t % beat_period) / beat_period
        
        def wave_val(center, width, height):
            d = phase - center
            return height * math.exp(-(d * d) / (2.0 * width * width))
        
        val = 0.0
        # P wave
        val += wave_val(0.15, 0.035, 0.18)
        # Q wave
        val += wave_val(0.28, 0.012, -0.12)
        # R peak
        val += wave_val(0.32, 0.015, 1.35)
        # S wave
        val += wave_val(0.36, 0.016, -0.28)
        # T wave
        val += wave_val(0.55, 0.065, 0.32)
        
        # Baseline wander (~0.25 Hz respiratory oscillation)
        if baseline_wander:
            val += 0.18 * math.sin(2 * math.pi * 0.25 * t) + 0.08 * math.sin(2 * math.pi * 0.12 * t)
            
        # 50 Hz powerline hum
        val += 0.015 * math.sin(2 * math.pi * 50.0 * t)
        
        # Random thermal noise
        val += random.gauss(0, noise_amplitude)
        
        signal[i] = round(val, 4)
        
    if NUMPY_AVAILABLE:
        return np.array(signal, dtype=float)
    return signal
