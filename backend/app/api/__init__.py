# -*- coding: utf-8 -*-
"""API package exports.
Ensures all routers are imported and listed in __all__ for main app inclusion.
"""

from app.api.auth import router as auth_router
from app.api.patients import router as patients_router
from app.api.ecg import router as ecg_router
from app.api.analysis import router as analysis_router
from app.api.caregivers import router as caregivers_router
from app.api.monitoring import router as monitoring_router
from app.api.health import router as health_router
from app.api.demo import router as demo_router
from app.api.ecg_preprocess import router as ecg_preprocess_router
from app.api.ecg_image import router as ecg_image_router
from app.api.datasets import router as datasets_router

__all__ = [
    "auth_router",
    "patients_router",
    "ecg_router",
    "analysis_router",
    "caregivers_router",
    "monitoring_router",
    "health_router",
    "demo_router",
    "ecg_preprocess_router",
    "ecg_image_router",
    "datasets_router",
]
