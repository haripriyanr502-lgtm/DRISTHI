# -*- coding: utf-8 -*-
"""Normal Sinus Rhythm (NSR) dataset adapter.

Implements discovery, header parsing, validation, and integrates with the
shared ECGRecord model from `common.py`.  The NSR collection stores each
recording as a WFDB trio (`.hea`, `.dat`, optional `.atr`).  Backup/auxiliary
header files (e.g. `*.hea-` or `*.hea--`) are ignored.  Raw and filtered
versions are *not* counted as separate physiological recordings – they are
represented as separate channels within a single ECGRecord.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Set

import wfdb

from .common import ECGRecord, LeadInfo

# ---------------------------------------------------------------------------
# Dataset root – relative to this file: backend/app/database/normal-sinus-rhythm-database
# ---------------------------------------------------------------------------
DATASET_ROOT: Path = (Path(__file__).resolve().parents[2] / "database" / "normal-sinus-rhythm-database")


def _parse_header(record: ECGRecord) -> None:
    """Populate ECGRecord fields from a WFDB header.

    On any parsing error the record is marked ``corrupt_header`` and a note is added.
    """
    stem = record.header_path.stem
    try:
        hdr = wfdb.rdheader(str(record.file_root / stem))
    except Exception as exc:
        record.validation_status = "corrupt_header"
        record.notes.append(f"Header parsing failed: {exc}")
        return

    # Sampling frequency
    record.sampling_frequency = float(hdr.fs) if hasattr(hdr, "fs") else 0.0

    # Lead information (name, gain, baseline, units)
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

    # Patient / subject identifier – the NSR filenames are numeric and serve as IDs.
    # If a comment line contains "Patient" we prefer that value.
    patient_id = record.recording_id
    for comment in getattr(hdr, "comments", []):
        if "Patient" in comment:
            tokens = comment.replace("#", "").split()
            for token in reversed(tokens):
                if token.isdigit():
                    patient_id = token
                    break
            break
    record.patient_id = patient_id

    record.validation_status = "header_parsed"


def _validate_files(record: ECGRecord) -> None:
    """Check that required files exist and update validation status."""
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
    """Recursively discover all valid NSR recordings.

    Returns
    -------
    List[ECGRecord]
        One record per unique physiological recording.  Duplicate/backup headers
        (e.g. *.hea-*, *.hea--) are ignored.
    """
    if not DATASET_ROOT.is_dir():
        # Dataset not present – return empty list instead of error
        return []
        raise FileNotFoundError(f"NSR dataset directory not found: {DATASET_ROOT}")

    records: List[ECGRecord] = []
    seen: Set[str] = set()

    for hea_path in DATASET_ROOT.rglob("*.hea"):
        # Skip backup/auxiliary files (ends with '-' or '--')
        if hea_path.name.endswith("-") or hea_path.name.endswith("--"):
            continue
        recording_id = hea_path.stem
        if recording_id in seen:
            continue
        seen.add(recording_id)

        dat_path = hea_path.with_suffix('.dat')
        atr_path = hea_path.with_suffix('.atr')
        atr_path = atr_path if atr_path.is_file() else None

        rec = ECGRecord(
            dataset_name="NSR",
            dataset_version=None,
            recording_id=recording_id,
            patient_id=None,
            file_root=hea_path.parent,
            header_path=hea_path,
            dat_path=dat_path,
            atr_path=atr_path,
        )
        _parse_header(rec)
        _validate_files(rec)
        rec.notes.append("dual_signal" if len(rec.lead_info) >= 2 else "single_signal")
        records.append(rec)

    return records


__all__ = ["discover", "DATASET_ROOT"]
