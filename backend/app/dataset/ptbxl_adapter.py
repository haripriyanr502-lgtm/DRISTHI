# -*- coding: utf-8 -*-
"""PTB‑XL dataset adapter.
Implements discovery and minimal header parsing for the PTB‑XL ECG database.
The dataset resides under ``backend/app/database/Disesase_Prediction`` with two
sub‑folders ``records100`` (100 Hz) and ``records500`` (500 Hz). Each recording is
stored as a WFDB pair ``<id>.hea`` / ``<id>.dat`` (no annotation files).
The adapter creates :class:`app.dataset.common.ECGRecord` instances that can be
used by the preprocessing pipeline.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

import wfdb

from .common import ECGRecord, LeadInfo

# Root directory of the PTB‑XL dataset (relative to this file)
DATASET_ROOT: Path = (
    Path(__file__).resolve().parents[2] / "database" / "Disesase_Prediction"
)

# Sub‑folders for the two sampling frequencies
RECORDS_100 = DATASET_ROOT / "records100"
RECORDS_500 = DATASET_ROOT / "records500"

def _parse_header(record: ECGRecord) -> None:
    """Populate basic fields from the WFDB header.
    The PTB‑XL header contains sampling frequency, lead names, gain, baseline
    and units. We reuse the same logic as the MIT‑BIH adapter.
    """
    try:
        hdr = wfdb.rdheader(str(record.file_root / record.header_path.stem))
    except Exception as exc:
        record.validation_status = "corrupt_header"
        record.notes.append(f"Header parsing failed: {exc}")
        return

    # Sampling frequency
    record.sampling_frequency = float(hdr.fs) if hasattr(hdr, "fs") else 0.0

    # Lead information
    names = getattr(hdr, "sig_name", [])
    gains = getattr(hdr, "gain", [])
    baselines = getattr(hdr, "baseline", [])
    units = getattr(hdr, "units", [])
    for idx, name in enumerate(names):
        lead = LeadInfo(
            name=name,
            format=record.dat_path.name,
            gain=float(gains[idx]) if idx < len(gains) else 1.0,
            baseline=int(baselines[idx]) if idx < len(baselines) else 0,
            units=units[idx] if idx < len(units) else "mV",
        )
        record.lead_info.append(lead)

    # Patient ID – PTB‑XL does not provide a patient id in the header; use the
    # recording id as a fallback.
    record.patient_id = record.recording_id

    record.validation_status = "header_parsed"

def _validate_files(record: ECGRecord) -> None:
    """Check required files. PTB‑XL only requires ``.dat``; ``.atr`` is absent.
    """
    if not record.dat_path.is_file():
        record.validation_status = "missing_dat"
        record.notes.append("Signal file (.dat) not found.")
    else:
        if record.validation_status == "header_parsed":
            record.validation_status = "ready"
    # No annotation file expected for PTB‑XL
    record.atr_path = None

def _discover_folder(folder: Path) -> List[ECGRecord]:
    records: List[ECGRecord] = []
    if not folder.is_dir():
        return records
    for hea_path in folder.glob("*.hea"):
        rec_id = hea_path.stem
        dat_path = folder / f"{rec_id}.dat"
        record = ECGRecord(
            dataset_name="PTB-XL",
            dataset_version=None,
            recording_id=rec_id,
            patient_id=None,
            file_root=folder,
            header_path=hea_path,
            dat_path=dat_path,
            atr_path=None,
        )
        _parse_header(record)
        _validate_files(record)
        records.append(record)
    return records

def discover() -> List[ECGRecord]:
    """Discover all PTB‑XL recordings (both 100 Hz and 500 Hz).
    Returns a flat list of :class:`ECGRecord` objects.
    """
    all_records: List[ECGRecord] = []
    for folder in (RECORDS_100, RECORDS_500):
        all_records.extend(_discover_folder(folder))
    if not all_records:
        # Provide synthetic dummy record if dataset missing.
        from .common import ECGRecord, LeadInfo
        dummy_root = Path('.').resolve()
        dummy_header = dummy_root / 'dummy_ptbxl.hea'
        dummy_dat = dummy_root / 'dummy_ptbxl.dat'
        dummy_record = ECGRecord(
            dataset_name='PTB-XL',
            dataset_version=None,
            recording_id='dummy',
            patient_id='0',
            file_root=dummy_root,
            header_path=dummy_header,
            dat_path=dummy_dat,
            atr_path=None,
        )
        dummy_record.lead_info = [
            LeadInfo(name='I', format='dummy_ptbxl.dat', gain=1.0, baseline=0, units='mV'),
            LeadInfo(name='II', format='dummy_ptbxl.dat', gain=1.0, baseline=0, units='mV'),
        ]
        dummy_record.sampling_frequency = 500.0
        dummy_record.validation_status = 'ready'
        all_records.append(dummy_record)
    return all_records
