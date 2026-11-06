import pytest
from app.dataset import nsr_adapter

def test_nsr_discovery():
    records = nsr_adapter.discover()
    assert records, "No NSR records discovered"
    for rec in records:
        assert rec.header_path.is_file()
        assert rec.dat_path.is_file()
        assert rec.validation_status in {"ready", "missing_dat", "corrupt_header"}

def test_nsr_no_duplicates():
    records = nsr_adapter.discover()
    ids = [r.recording_id for r in records]
    assert len(ids) == len(set(ids)), "Duplicate recording IDs detected"
