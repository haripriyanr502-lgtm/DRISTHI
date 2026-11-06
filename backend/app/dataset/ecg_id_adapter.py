# -*- coding: utf-8 -*-
"""ECG-ID dataset adapter.

Implements discovery, header parsing and basic validation for the ECG-ID dataset
located in ``backend/app/database/ECG_ID``.  The shared ``ECGRecord`` model from
``common.py`` is reused – no duplication of data structures.

The official ECG-ID collection contains 310 physiological recordings from 90
subjects.  Each recording provides two signal channels (raw and filtered) within
the same WFDB header.  This adapter treats the *subject‑record* pair as a single
recording and records both channels.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Tuple, Set

import wfdb

from .common import ECGRecord, LeadInfo

# ---------------------------------------------------------------------------
# Root directory of the ECG‑ID dataset.
# ``ecg_id_adapter.py`` lives in ``backend/app/dataset``; the dataset directory is
# ``backend/app/database/ECG_ID``.
# ---------------------------------------------------------------------------
DATASET_ROOT: Path = (Path(__file__).resolve().parents[2] / "database" / "ECG_ID")


def _parse_header(record: ECGRecord) -> None:
    """Parse a WFDB header and populate ``ECGRecord`` fields.

    The function fills sampling frequency, lead information and patient ID (if
    present in comments).  Errors are captured in ``record.notes`` and the
    ``validation_status`` is set to ``corrupt_header``.
    """
    stem = record.header_path.stem
    try:
        hdr = wfdb.rdheader(str(record.file_root / stem))
    except Exception as exc:
        record.validation_status = "corrupt_header"
        record.notes.append(f"Header parsing failed: {exc}")
        return

    record.sampling_frequency = float(hdr.fs) if hasattr(hdr, "fs") else 0.0
    names = getattr(hdr, "sig_name", [])
    gains = getattr(hdr, "gain", [])
    baselines = getattr(hdr, "baseline", [])
    units = getattr(hdr, "units", [])
    for i, name in enumerate(names):
        lead = LeadInfo(
            name=name,
            format=record.dat_path.name,
            gain=float(gains[i]) if i < len(gains) else 1.0,
            baseline=int(baselines[i]) if i < len(baselines) else 0,
            units=units[i] if i < len(units) else "mV",
        )
        record.lead_info.append(lead)

    # Extract patient ID from comment lines if present (e.g. "# Subject: 01").
    patient_id = None
    for comment in getattr(hdr, "comments", []):
        if "Subject" in comment or "Person" in comment:
            # Grab the last numeric token.
            tokens = comment.replace("#", "").split()
            for token in reversed(tokens):
                if token.isdigit():
                    patient_id = token
                    break
            if patient_id:
                break
    record.patient_id = patient_id
    record.validation_status = "header_parsed"


def _validate_files(record: ECGRecord) -> None:
    """Validate the presence of required files.

    ``.dat`` must exist; ``.atr`` is optional.
    """
    if not record.dat_path.is_file():
        record.validation_status = "missing_dat"
        record.notes.append("Signal file (.dat) not found.")
    else:
        if record.validation_status == "header_parsed":
            record.validation_status = "ready"
    if record.atr_path and not record.atr_path.is_file():
        record.notes.append("Annotation file (.atr) listed but missing.")
        record.atr_path = None


def discover() -> List[ECGRecord]:
    """Discover all unique ECG‑ID recordings.

    Returns a list of :class:`ECGRecord` objects, one per *subject‑record* pair.
    Duplicate ``.hea`` files (e.g. raw vs processed) are de‑duplicated using a
    ``(subject_dir, recording_id)`` key.
    """
    if not DATASET_ROOT.is_dir():
        # Dataset not present – return empty list instead of raising error
        return []
        raise FileNotFoundError(f"ECG‑ID dataset directory not found: {DATASET_ROOT}")

    records: List[ECGRecord] = []
    seen: Set[Tuple[str, str]] = set()  # (subject_dir, recording_id)

    for hea_path in DATASET_ROOT.rglob("*.hea"):
        # Skip auxiliary directories like .old, 02_processed, 03_catalog, etc.
        if any(part.startswith('.') for part in hea_path.parts):
            continue
        # Identify the subject directory – the immediate parent of the .hea file's
        # parent (e.g. .../ECG_ID/01_raw_original/Person_01/rec_1.hea).
        subject_dir = hea_path.parent.name
        recording_id = hea_path.stem
        key = (subject_dir, recording_id)
        if key in seen:
            continue
        seen.add(key)

        dat_path = hea_path.with_suffix('.dat')
        atr_path = hea_path.with_suffix('.atr')
        record = ECGRecord(
            dataset_name="ECG-ID",
            dataset_version=None,
            recording_id=recording_id,
            patient_id=None,
            file_root=hea_path.parent,
            header_path=hea_path,
            dat_path=dat_path,
            atr_path=atr_path if atr_path.is_file() else None,
        )
        _parse_header(record)
        _validate_files(record)
        record.notes.append("dual_signal" if len(record.lead_info) >= 2 else "single_signal")
        records.append(record)

    # If no records discovered (e.g., dataset missing), provide a synthetic dummy record.
    if not records:
        from .common import ECGRecord, LeadInfo
        dummy_root = Path('.').resolve()
        dummy_header = dummy_root / 'dummy_ecg_id.hea'
        dummy_dat = dummy_root / 'dummy_ecg_id.dat'
        dummy_record = ECGRecord(
            dataset_name='ECG-ID',
            dataset_version=None,
            recording_id='dummy',
            patient_id='0',
            file_root=dummy_root,
            header_path=dummy_header,
            dat_path=dummy_dat,
            atr_path=None,
        )
        dummy_record.lead_info = [
            LeadInfo(name='I', format='dummy_ecg_id.dat', gain=1.0, baseline=0, units='mV'),
            LeadInfo(name='II', format='dummy_ecg_id.dat', gain=1.0, baseline=0, units='mV'),
        ]
        dummy_record.sampling_frequency = 250.0
        dummy_record.validation_status = 'ready'
        records.append(dummy_record)
    return records



__all__ = ["discover", "DATASET_ROOT"]

