# -*- coding: utf-8 -*-
"""FastAPI router exposing ECG preprocessing service.

Endpoint:
    POST /ecg/preprocess
Accepts a JSON payload with a numeric ECG signal (list of samples per lead),
original sampling rate, and optional preprocessing configuration.
Returns the processed signal plus before/after quality metrics and any warnings.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.ecg_preprocess_service import preprocess_signal

router = APIRouter(prefix="/ecg", tags=["ECG Preprocessing"])

@router.post("/preprocess")
def preprocess_ecg(payload: Dict[str, Any]):
    """Run the ECG preprocessing pipeline.

    Expected JSON keys:
        - ``signal``: List[List[float]] – ECG samples (either lead‑wise or sample‑wise).
        - ``sampling_rate``: float – original Hz.
        - ``config`` (optional): dict – preprocessing configuration (see service docs).
    """
    signal = payload.get("signal")
    sr = payload.get("sampling_rate")
    config = payload.get("config") or {}
    if signal is None or sr is None:
        raise HTTPException(status_code=400, detail="Missing 'signal' or 'sampling_rate' in payload.")
    try:
        result = preprocess_signal(signal, float(sr), config)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return result

