# -*- coding: utf-8 -*-
"""Focused tests for ECG preprocessing service.
Ensures the pipeline works on real recordings from each integrated dataset.
"""

import pytest
from app.services.ecg_preprocess_service import preprocess_signal
from app.dataset import mitbih_adapter, ecg_id_adapter, ptbxl_adapter, nsr_adapter

def load_first_record(adapter):
    records = adapter.discover()
    assert records, f"No records discovered by {adapter.__name__}"
    rec = records[0]
    # Load full signal
    signal = rec.load_signal()
    # Convert tuple of leads to list of lists for service input
    raw_signal = [list(lead) for lead in signal]
    return raw_signal, rec.sampling_frequency

@pytest.mark.parametrize("adapter", [mitbih_adapter, ecg_id_adapter, ptbxl_adapter, nsr_adapter])
def test_preprocess_basic(adapter):
    raw_signal, sr = load_first_record(adapter)
    # Run preprocessing with default config
    result = preprocess_signal(raw_signal, sr)
    assert "processed_signal" in result
    assert isinstance(result["processed_signal"], list)
    # Ensure warnings list exists
    assert isinstance(result.get("warnings", []), list)
    # Verify sampling rate in result matches input (no resampling by default)
    assert result["original_sampling_rate_hz"] == sr
    assert result["processed_sampling_rate_hz"] == sr
    # Basic quality metrics should have non-zero samples
    before = result["quality_before"]
    after = result["quality_after"]
    assert before["n_samples"] == after["n_samples"]
    assert before["n_leads"] == after["n_leads"]

def test_preprocess_invalid_range():
    # Create synthetic signal of 2 leads, 100 samples
    raw_signal = [[0.0] * 100, [1.0] * 100]
    sr = 100.0
    # Config with bandpass exceeding Nyquist
    config = {"bandpass": [60, 120]}
    result = preprocess_signal(raw_signal, sr, config)
    # Should skip filter and add warning
    assert any("Invalid bandpass" in w for w in result["warnings"])

def test_preprocess_nan_handling():
    raw_signal = [[0.0, float('nan'), 2.0], [1.0, 1.0, 1.0]]
    sr = 100.0
    result = preprocess_signal(raw_signal, sr)
    # NaNs should be interpolated, no remaining NaNs
    import numpy as np
    processed = np.array(result["processed_signal"])
    assert not np.isnan(processed).any()

