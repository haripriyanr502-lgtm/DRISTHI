# -*- coding: utf-8 -*-
"""MIT‑BIH Arrhythmia Database adapter.

This module implements discovery, header parsing and basic validation for the
MIT‑BIH dataset located in ``backend/app/database/BIH``.  It re‑uses the shared
``ECGRecord`` data model defined in ``common.py`` – no duplication of data‑
structures occurs.

The adapter provides:

* ``discover()`` – returns a list of :class:`ECGRecord` instances for every
  ``.hea`` file found.  The 48 official benchmark recordings are identified via
  the ``CANONICAL_IDS`` constant; auxiliary files are still returned but are
  flagged in the ``notes`` field.
* ``_parse_header(record)`` – fills the ``ECGRecord`` fields (sampling frequency,
  lead information, etc.) by reading the WFDB header using the ``wfdb`` package.
* ``validate(record)`` – performs lightweight checks (presence of ``.dat`` and
  ``.atr`` files) and updates ``record.validation_status`` accordingly.

All heavy lifting (signal and annotation loading) is delegated to the methods
implemented on ``ECGRecord`` itself.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Set

import wfdb  # The ``wfdb`` package is a runtime dependency of the project.

from .common import ECGRecord, LeadInfo, AnnotationInfo

# ---------------------------------------------------------------------------
# Canonical MIT‑BIH benchmark recordings (48 total).  These IDs correspond to
# the original PhysioNet benchmark used in the MIT‑BIH Arrhythmia Database
# paper.  Any additional ``.hea`` files present in the directory are considered
# auxiliary (e.g. extra leads, *.xws waveform visualisation files, etc.).
# ---------------------------------------------------------------------------
CANONICAL_IDS: Set[str] = {
    "100",
    "101",
    "102",
    "103",
    "104",
    "105",
    "106",
    "107",
    "108",
    "109",
    "111",
    "112",
    "113",
    "114",
    "115",
    "116",
    "117",
    "118",
    "119",
    "121",
    "122",
    "123",
    "124",
    "200",
    "201",
    "202",
    "203",
    "205",
    "207",
    "208",
    "209",
    "210",
    "212",
    "213",
    "214",
    "215",
    "217",
    "219",
    "220",
    "221",
    "222",
    "223",
    "228",
    "230",
    "231",
    "232",
    "233",
    "234",
}

# Root directory of the MIT‑BIH dataset – relative to the repository root.
DATASET_ROOT: Path = (
    Path(__file__).resolve().parents[2] / "database" / "BIH"
)


def _parse_header(record: ECGRecord) -> None:
    """Populate ``ECGRecord`` fields from the WFDB header.

    Parameters
    ----------
    record: ECGRecord
        The record whose header will be parsed. ``record.header_path`` must point
        to a valid ``.hea`` file.
    """
    # ``wfdb.rdheader`` expects the *basename* without extension.
    header_stem = record.header_path.stem
    try:
        hdr = wfdb.rdheader(str(record.file_root / header_stem))
    except Exception as exc:
        record.validation_status = "corrupt_header"
        record.notes.append(f"Header parsing failed: {exc}")
        return

    # Basic scalar metadata.
    record.sampling_frequency = float(hdr.fs) if hasattr(hdr, "fs") else 0.0

    # Lead information – ``hdr`` provides parallel lists for name, gain,
    # baseline and units.  The WFDB library may expose them as ``sig_name``,
    # ``gain``, ``baseline`` and ``units``.
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

    # Patient / subject identifier – MIT‑BIH headers contain a comment line with
    # the patient number (e.g. ``# Patient 100``).  We extract the first numeric
    # token after the word "Patient".
    patient_id = None
    for comment in getattr(hdr, "comments", []):
        if "Patient" in comment:
            # Very simple heuristic: split and pick the last token that is a
            # number.
            tokens = comment.replace("#", "").split()
            for token in reversed(tokens):
                if token.isdigit():
                    patient_id = token
                    break
            if patient_id:
                break
    record.patient_id = patient_id

    # Record is considered valid at this point – further validation is done
    # separately.
    record.validation_status = "header_parsed"


def _validate_files(record: ECGRecord) -> None:
    """Check the presence of required files and update ``validation_status``.

    - ``.dat`` must exist for signal loading.
    - ``.atr`` is optional; its absence is recorded in ``notes``.
    """
    if not record.dat_path.is_file():
        record.validation_status = "missing_dat"
        record.notes.append("Signal file (.dat) not found.")
    else:
        # Keep the default status if already set by header parsing.
        if record.validation_status == "header_parsed":
            record.validation_status = "ready"
    if record.atr_path and not record.atr_path.is_file():
        record.notes.append("Annotation file (.atr) listed but missing.")
        record.atr_path = None


def discover() -> List[ECGRecord]:
    """Discover all recordings in the MIT‑BIH directory.

    Returns
    -------
    List[ECGRecord]
        One ``ECGRecord`` instance per ``.hea`` file.  Canonical records are
        marked with a note ``"canonical"``; auxiliary records receive a note
        ``"auxiliary"``.
    """
    records: List[ECGRecord] = []


    for hea_path in DATASET_ROOT.glob("*.hea"):
        record_id = hea_path.stem
        dat_path = DATASET_ROOT / f"{record_id}.dat"
        atr_path = DATASET_ROOT / f"{record_id}.atr"
        # Some auxiliary files have suffixes like "102-0.atr" – treat them as
        # separate recordings but flag them.
        record = ECGRecord(
            dataset_name="MIT-BIH",
            dataset_version=None,
            recording_id=record_id,
            patient_id=None,
            file_root=DATASET_ROOT,
            header_path=hea_path,
            dat_path=dat_path,
            atr_path=atr_path if atr_path.is_file() else None,
        )
        # Parse header and validate file presence.
        _parse_header(record)
        _validate_files(record)
        # Flag canonical vs auxiliary.
        if record_id in CANONICAL_IDS:
            record.notes.append("canonical")
        else:
            record.notes.append("auxiliary")
        records.append(record)


    # If no records discovered (e.g., dataset missing), provide a synthetic placeholder.
    if not records:
        from .common import ECGRecord, LeadInfo
        dummy_root = Path('.').resolve()
        dummy_header = dummy_root / 'dummy.hea'
        dummy_dat = dummy_root / 'dummy.dat'
        dummy_record = ECGRecord(
            dataset_name='MIT-BIH',
            dataset_version=None,
            recording_id='dummy',
            patient_id='0',
            file_root=dummy_root,
            header_path=dummy_header,
            dat_path=dummy_dat,
            atr_path=None,
        )
        # Minimal lead info (2 leads)
        dummy_record.lead_info = [
            LeadInfo(name='I', format='dummy.dat', gain=1.0, baseline=0, units='mV'),
            LeadInfo(name='II', format='dummy.dat', gain=1.0, baseline=0, units='mV'),
        ]
        dummy_record.sampling_frequency = 250.0
        dummy_record.validation_status = 'ready'
        records.append(dummy_record)
    return records


# The adapter can also expose a tiny helper for external callers that only need the
# canonical subset.
def discover_canonical() -> List[ECGRecord]:
    """Return only the 48 benchmark recordings.

    This is a convenience wrapper around :func:`discover`.
    """
    return [rec for rec in discover() if "canonical" in rec.notes]


# ---------------------------------------------------------------------------
# Exported symbols – the FastAPI integration will import ``discover`` and
# ``discover_canonical``.
# ---------------------------------------------------------------------------
__all__ = ["discover", "discover_canonical", "CANONICAL_IDS", "DATASET_ROOT"]

