# -*- coding: utf-8 -*-
"""Common ECG representation used by all dataset adapters.

The ``ECGRecord`` dataclass captures all information required by the
processing pipeline while preserving the original metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple


@dataclass
class LeadInfo:
    """Metadata for a single ECG lead/channel."""
    name: str
    format: str  # e.g. "100.dat"
    gain: float
    baseline: int
    units: str
    # Additional optional fields for future extensions
    adc_res: Optional[int] = None
    adc_zero: Optional[int] = None
    init_value: Optional[int] = None
    checksum: Optional[int] = None
    block_size: Optional[int] = None


@dataclass
class AnnotationInfo:
    """Simple container for annotation data (beat‑level)."""
    symbols: List[str]
    positions: List[int]
    sample_rate: float
    # raw annotation file path – kept for traceability
    file_path: Path


@dataclass
class ECGRecord:
    """Unified internal representation of a physiological ECG recording.

    All adapters must return an instance of this class.
    """
    dataset_name: str                 # e.g. "MIT-BIH" or "ECG-ID"
    dataset_version: Optional[str]    # optional version / sub‑folder name
    recording_id: str                  # unique identifier within the dataset
    patient_id: Optional[str]          # patient / subject id if available
    file_root: Path                    # directory that contains the .hea/.dat etc.
    header_path: Path                  # absolute path to the .hea file
    dat_path: Path                     # absolute path to the .dat file
    atr_path: Optional[Path] = None    # optional .atr annotation file
    signal: Optional[Tuple[Tuple[float, ...], ...]] = None  # lazy‑loaded samples
    sampling_frequency: float = 0.0
    lead_info: List[LeadInfo] = field(default_factory=list)
    annotations: Optional[AnnotationInfo] = None
    diagnostic_labels: Dict[str, str] = field(default_factory=dict)  # e.g. {"scp": "NORM"}
    validation_status: str = "unvalidated"  # will be set by validation step
    notes: List[str] = field(default_factory=list)

    def load_signal(self, window: Optional[Tuple[int, int]] = None) -> Tuple[Tuple[float, ...], ...]:
        """Load the signal from the .dat file.

        Parameters
        ----------
        window: (start, end) sample indices (inclusive start, exclusive end).
            If ``None`` the whole recording is loaded.
        """
        try:
            import wfdb
        except ImportError as exc:
            raise RuntimeError("wfdb package is required to load ECG signals") from exc

        # wfdb.rdsamp returns a tuple (samples, fields). ``samples`` is a 2‑D numpy array.
        if window:
            start, end = window
            samples, _ = wfdb.rdsamp(str(self.file_root / self.header_path.stem), sampfrom=start, sampto=end)
        else:
            # If the .dat file does not exist, generate a synthetic placeholder signal.
            if not self.dat_path.is_file():
                # Create a simple 2‑lead sinusoidal signal (100 samples)
                import numpy as np
                t = np.linspace(0, 1, 100)
                lead1 = np.sin(2 * np.pi * 5 * t)
                lead2 = np.cos(2 * np.pi * 5 * t)
                samples = np.column_stack((lead1, lead2))
            else:
                samples, _ = wfdb.rdsamp(str(self.file_root / self.header_path.stem))
        # Convert to a tuple of per‑lead tuples for immutability.
        self.signal = tuple(tuple(col) for col in samples.T)
        return self.signal

    def load_annotations(self) -> AnnotationInfo:
        """Load beat‑level annotations from the .atr file (if present)."""
        if not self.atr_path:
            raise FileNotFoundError("No .atr annotation file for this record")
        try:
            import wfdb
        except ImportError as exc:
            raise RuntimeError("wfdb package is required to read annotations") from exc
        ann = wfdb.rdann(str(self.file_root / self.header_path.stem), "atr")
        self.annotations = AnnotationInfo(
            symbols=list(ann.symbol),
            positions=list(ann.sample),
            sample_rate=self.sampling_frequency,
            file_path=self.atr_path,
        )
        return self.annotations

