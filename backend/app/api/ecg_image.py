from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

from app.services.ecg_image_service import process_ecg_image

router = APIRouter()

@router.post("/upload_image")
def upload_ecg_image(
    file: UploadFile = File(...),
    speed_mm_s: Optional[float] = Form(None),
    amp_mm_mv: Optional[float] = Form(None),
):
    """Upload an ECG paper image and return extracted waveform data.

    Supported formats: JPG, JPEG, PNG.
    """
    # Read the uploaded file into memory
    content = file.file.read()
    result = process_ecg_image(content, speed_mm_s=speed_mm_s, amp_mm_mv=amp_mm_mv)
    return result

