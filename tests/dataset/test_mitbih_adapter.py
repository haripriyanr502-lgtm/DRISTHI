# -*- coding: utf-8 -*-
"""Tests for the MIT‑BIH dataset adapter.

These tests verify discovery, canonical‑record identification, header parsing,
signal loading and optional annotation loading.  They run against the actual
dataset files shipped with the repository – no modification of the source data
occurs.
"""

import pathlib

import pytest

from backend.app.dataset.mitbih_adapter import discover, discover_canonical, CANONICAL_IDS, DATASET_ROOT

@pytest.fixture(scope="module")
def all_records():
    return discover()

def test_discover_counts(all_records):
    # The repository contains exactly the 48 benchmark ``.hea`` files.
    assert len(all_records) == 48, "Expected 48 .hea files in the MIT‑BIH directory"
    # All records should have a header_path ending with .hea
    for rec in all_records:
        assert rec.header_path.suffix == ".hea"

def test_canonical_identification(all_records):
    canonical = [rec for rec in all_records if "canonical" in rec.notes]
    assert len(canonical) == len(CANONICAL_IDS), "Canonical count mismatch"
    # Ensure each canonical ID is present.
    canonical_ids = {rec.recording_id for rec in canonical}
    assert canonical_ids == CANONICAL_IDS

def test_header_parsing_and_validation(all_records):
    for rec in all_records:
        # Header should have been parsed.
        assert rec.validation_status in {"ready", "header_parsed"}, f"Record {rec.recording_id} not parsed"
        # Sampling frequency should be a positive float (MIT‑BIH uses 360 Hz).
        assert rec.sampling_frequency > 0, f"Record {rec.recording_id} missing sampling frequency"
        # At least one lead must be discovered.
        assert len(rec.lead_info) >= 1
        # .dat file must exist for ready records.
        if rec.validation_status == "ready":
            assert rec.dat_path.is_file()

def test_signal_loading():
    # Pick a known canonical record – 100 is always present.
    record_id = "100"
    rec = next(r for r in discover_canonical() if r.recording_id == record_id)
    # Load the full signal; it should return a tuple of per‑lead tuples.
    sig = rec.load_signal()
    assert isinstance(sig, tuple)
    assert len(sig) == len(rec.lead_info)
    # Ensure there is at least one sample.
    assert len(sig[0]) > 0

def test_annotation_loading():
    # Record 100 has an annotation file.
    rec = next(r for r in discover_canonical() if r.recording_id == "100")
    if rec.atr_path:
        ann = rec.load_annotations()
        assert isinstance(ann, type(rec.annotations))
        assert len(ann.symbols) == len(ann.positions)
    else:
        pytest.skip("No .atr file for record 100 in this repository")

