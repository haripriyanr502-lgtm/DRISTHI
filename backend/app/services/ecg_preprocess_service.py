# -*- coding: utf-8 -*-
"""ECG preprocessing service.

Provides a configurable pipeline for cleaning numerical ECG signals.
The pipeline is deliberately lightweight and does not perform any
machine‑learning or diagnostic analysis – it prepares signals for
subsequent modeling stages.
"""

from __future__ import annotations

import numpy as np
from scipy import signal
from typing import Dict, List, Tuple, Optional

# ---------------------------------------------------------------------------
# Helper utilities for quality metrics
# ---------------------------------------------------------------------------

def _quality_metrics(samples: np.ndarray, sampling_rate: float) -> Dict:
    """Calculate basic quality information for a signal.

    Parameters
    ----------
    samples : np.ndarray
        2‑D array ``(n_samples, n_leads)``.
    sampling_rate : float
        Hz.
    """
    n_samples, n_leads = samples.shape
    duration = n_samples / sampling_rate if sampling_rate else 0.0
    # Missing/invalid values count
    invalid = np.isnan(samples) | np.isinf(samples)
    n_invalid = int(invalid.sum())
    # Amplitude range per lead
    amp_min = np.nanmin(samples, axis=0).tolist()
    amp_max = np.nanmax(samples, axis=0).tolist()
    return {
        "sampling_rate_hz": sampling_rate,
        "n_samples": n_samples,
        "n_leads": n_leads,
        "duration_seconds": duration,
        "invalid_samples": n_invalid,
        "amplitude_min_mv": amp_min,
        "amplitude_max_mv": amp_max,
    }

# ---------------------------------------------------------------------------
# Core preprocessing pipeline
# ---------------------------------------------------------------------------

def preprocess_signal(
    raw_signal: List[List[float]],
    original_sampling_rate: float,
    config: Optional[Dict] = None,
) -> Dict:
    """Preprocess a numeric ECG signal.

    Parameters
    ----------
    raw_signal : List[List[float]]
        Signal as a list of lead‑wise samples ``[[lead1...], [lead2...]]`` **or**
        a list of time‑ordered samples ``[[s1_lead1, s1_lead2, ...], ...]``.
        The function normalises both representations to a ``(n_samples, n_leads)``
        NumPy array.
    original_sampling_rate : float
        Sampling frequency of the input signal (Hz).
    config : dict, optional
        Configuration dictionary. Keys (all optional):
        * ``baseline_wander_cutoff`` – high‑pass cutoff (Hz) for baseline removal.
        * ``powerline_notch`` – ``True``/``False`` to apply 50 Hz notch filter.
        * ``lowpass_cutoff`` – low‑pass cutoff (Hz) for high‑frequency noise.
        * ``bandpass`` – ``[low, high]`` Hz tuple to apply a band‑pass filter.
        * ``target_sampling_rate`` – if set, signal will be resampled to this rate.
        * ``normalize`` – ``True``/``False`` to scale each lead to zero‑mean, unit‑std.
    Returns
    -------
    dict
        Contains original metadata, processed signal (as list of lists), the
        configuration used, before/after quality metrics and any warnings.
    """
    if config is None:
        config = {}

    warnings: List[str] = []

    # -------------------------------------------------------------------
    # Normalise input shape to (samples, leads)
    # -------------------------------------------------------------------
    arr = np.array(raw_signal, dtype=float)
    if arr.ndim == 2:
        if arr.shape[0] < arr.shape[1]:
            # Assume shape (leads, samples) – transpose
            arr = arr.T
    else:
        raise ValueError("Raw signal must be a 2‑D array of samples and leads.")

    # Validate input: missing or non‑finite values
    if np.isnan(arr).any() or np.isinf(arr).any():
        warnings.append("Input contains NaN or infinite values; they will be interpolated.")
        # Simple linear interpolation for NaNs per lead
        for lead_idx in range(arr.shape[1]):
            lead = arr[:, lead_idx]
            nans = np.isnan(lead) | np.isinf(lead)
            if nans.any():
                x = np.arange(len(lead))
                lead[nans] = np.interp(x[nans], x[~nans], lead[~nans])
                arr[:, lead_idx] = lead

    before_metrics = _quality_metrics(arr, original_sampling_rate)

    # -------------------------------------------------------------------
    # Guard for very short signals (<=9 samples) – skip all filtering steps.
    # -------------------------------------------------------------------
    if arr.shape[0] <= 9:
        warnings.append("Signal too short for filtering; all filters skipped.")
    else:
        # Baseline wander removal (high‑pass filter)
        hp_cutoff = config.get("baseline_wander_cutoff", 0.5)  # Hz, typical
        if hp_cutoff and hp_cutoff > 0:
            nyq = 0.5 * original_sampling_rate
            if hp_cutoff < nyq:
                b, a = signal.butter(2, hp_cutoff / nyq, btype="high")
                arr = signal.filtfilt(b, a, arr, axis=0)
            else:
                warnings.append("Baseline wander cutoff exceeds Nyquist; skipped.")

        # Power‑line notch filter (50 Hz)
        if config.get("powerline_notch", True):
            f0 = 50.0
            q = 30.0  # quality factor
            nyq = 0.5 * original_sampling_rate
            if f0 < nyq:
                w0 = f0 / nyq
                b, a = signal.iirnotch(w0, q)
                arr = signal.filtfilt(b, a, arr, axis=0)
            else:
                warnings.append("Power‑line frequency exceeds Nyquist; notch filter skipped.")

        # Low‑pass or band‑pass filtering
        if "bandpass" in config:
            low, high = config["bandpass"]
            nyq = 0.5 * original_sampling_rate
            low_norm = low / nyq
            high_norm = high / nyq
            if 0 < low_norm < high_norm < 1:
                b, a = signal.butter(2, [low_norm, high_norm], btype="band")
                arr = signal.filtfilt(b, a, arr, axis=0)
            else:
                warnings.append("Invalid bandpass configuration; filter skipped.")
        else:
            # Apply low‑pass if configured
            lp_cutoff = config.get("lowpass_cutoff", 40.0)
            if lp_cutoff and lp_cutoff > 0:
                nyq = 0.5 * original_sampling_rate
                if lp_cutoff < nyq:
                    b, a = signal.butter(2, lp_cutoff / nyq, btype="low")
                    arr = signal.filtfilt(b, a, arr, axis=0)
                else:
                    warnings.append("Low‑pass cutoff exceeds Nyquist; skipped.")

    # -------------------------------------------------------------------
    # Resampling if requested
    # -------------------------------------------------------------------
    target_sr = config.get("target_sampling_rate")
    resampled = False
    new_sr = original_sampling_rate
    if target_sr and target_sr != original_sampling_rate:
        # Use polyphase resampling for efficiency
        gcd = np.gcd(int(original_sampling_rate), int(target_sr))
        up = int(target_sr // gcd)
        down = int(original_sampling_rate // gcd)
        arr = signal.resample_poly(arr, up, down, axis=0)
        new_sr = target_sr
        resampled = True
        warnings.append(f"Signal resampled from {original_sampling_rate} Hz to {target_sr} Hz.")

    # -------------------------------------------------------------------
    # Normalisation (zero‑mean, unit‑std) – optional
    # -------------------------------------------------------------------
    if config.get("normalize", False):
        mean = np.mean(arr, axis=0)
        std = np.std(arr, axis=0)
        std[std == 0] = 1.0
        arr = (arr - mean) / std
        warnings.append("Signal normalised to zero mean and unit variance per lead.")

    after_metrics = _quality_metrics(arr, new_sr)

    # Convert processed signal back to list of lists for JSON serialisation
    processed_signal = arr.tolist()

    result = {
        "original_sampling_rate_hz": original_sampling_rate,
        "processed_sampling_rate_hz": new_sr,
        "config_used": config,
        "warnings": warnings,
        "quality_before": before_metrics,
        "quality_after": after_metrics,
        "processed_signal": processed_signal,
    }
    return result

# End of file

