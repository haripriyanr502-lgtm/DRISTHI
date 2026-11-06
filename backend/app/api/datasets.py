# -*- coding: utf-8 -*-
"""Dataset router exposing discovered records for each integrated dataset."""

from fastapi import APIRouter
from typing import List, Dict

from app.dataset import nsr_adapter

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.get("/nsr")
def list_nsr() -> List[Dict]:
    """Return a concise list of NSR records."""
    return [
        {
            "recording_id": r.recording_id,
            "patient_id": r.patient_id,
            "validation_status": r.validation_status,
            "sampling_frequency": r.sampling_frequency,
            "lead_count": len(r.lead_info),
            "has_annotation": bool(r.atr_path),
        }
        for r in nsr_adapter.discover()
    ]
