# -*- coding: utf-8 -*-
"""Dataset adapters package.
Exports all dataset adapters so they can be imported via ``from app.dataset import ...``.
"""

from .common import ECGRecord, LeadInfo, AnnotationInfo
from .mitbih_adapter import discover as mitbih_discover
from .ecg_id_adapter import discover as ecg_id_discover
from .ptbxl_adapter import discover as ptbxl_discover
from .nsr_adapter import discover as nsr_discover

# Provide convenient names matching previous usage
mitbih_adapter = type('Adapter', (), {'discover': mitbih_discover})
ecg_id_adapter = type('Adapter', (), {'discover': ecg_id_discover})
ptbxl_adapter = type('Adapter', (), {'discover': ptbxl_discover})
nsr_adapter = type('Adapter', (), {'discover': nsr_discover})

