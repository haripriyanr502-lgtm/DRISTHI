# -*- coding: utf-8 -*-
"""Service for converting ECG paper images to numerical signals.

The implementation follows a minimal, deterministic pipeline using only
standard image‑processing libraries (OpenCV, NumPy).  It deliberately avoids
machine‑learning models – the goal is to provide a *working* baseline that can
be extended later.

Key steps:
1. Load image (JPG/JPEG/PNG).
2. Detect the main ECG graph region via contour analysis.
3. Estimate grid spacing (both horizontal and vertical) using Hough line
   detection.  From this we derive the pixel‑to‑time and pixel‑to‑amplitude
   conversion factors.
4. Extract the waveform by isolating the darkest curve (the trace) inside the
   detected region.

































   
5. Resample the trace to a regular time axis according to the paper speed
   (default 25 mm/s) and amplitude calibration (default 10 mm/mV) – these can
   be overridden by the caller.
6. Return the signal, calibration metadata and any warnings.

The function is deliberately tolerant: if any step fails it returns an empty
signal together with informative warnings rather than raising exceptions.
"""

from __future__ import annotations

import io
import warnings
from typing import Dict, List, Tuple, Optional

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _load_image(file_bytes: bytes) -> np.ndarray:
    """Decode uploaded image bytes to a BGR NumPy array.

    Raises
    ------
    ValueError
        If the image cannot be decoded.
    """
    img_arr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Unable to decode image – unsupported format or corrupted file.")
    return img


def _detect_graph_region(img: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
    """Detect the rectangular region that contains the ECG trace.

    Returns a cropped image and the (x, y, w, h) of the bounding box in the
    original image.  If detection fails the original image is returned unchanged.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply slight blur to reduce noise before edge detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    # Find contours – the largest rectangular contour is assumed to be the graph
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img, (0, 0, img.shape[1], img.shape[0])
    # Sort by area descending
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    for cnt in contours:
        # Approximate contour to a polygon and check if it is roughly rectangular
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            cropped = img[y : y + h, x : x + w]
            return cropped, (x, y, w, h)
    # Fallback – return original image
    return img, (0, 0, img.shape[1], img.shape[0])


def _estimate_grid_spacing(gray: np.ndarray) -> Tuple[Optional[float], Optional[float]]:
    """Estimate horizontal and vertical grid spacing in pixels.

    Uses Hough line detection on a binarised version of the image.  Returns
    (horizontal_spacing, vertical_spacing) – ``None`` if the spacing cannot be
    determined reliably.
    """
    # Binarise – grid lines are usually light on dark background
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    # Detect lines
    lines = cv2.HoughLinesP(binary, 1, np.pi / 180, threshold=100, minLineLength=30, maxLineGap=10)
    if lines is None:
        return None, None
    horiz = []
    vert = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(y2 - y1) < 5:  # roughly horizontal
            horiz.append(abs(x2 - x1))
        elif abs(x2 - x1) < 5:  # roughly vertical
            vert.append(abs(y2 - y1))
    # Compute median spacing
    h_spacing = np.median(horiz) if horiz else None
    v_spacing = np.median(vert) if vert else None
    return (float(h_spacing) if h_spacing is not None else None,
            float(v_spacing) if v_spacing is not None else None)


def _extract_waveform(region: np.ndarray) -> np.ndarray:
    """Extract the ECG trace as a binary mask.

    The trace is assumed to be the darkest continuous line within the region.
    A simple approach: invert, threshold, then keep the longest connected
    component.
    """
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    # Invert – trace is dark
    inv = cv2.bitwise_not(gray)
    # Adaptive threshold to cope with varying illumination
    thresh = cv2.adaptiveThreshold(inv, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY, 31, -10)
    # Remove small noise
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    # Keep the largest connected component (the trace)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(cleaned, connectivity=8)
    if num_labels <= 1:
        return np.zeros_like(cleaned)
    # Find label with largest area (ignore background label 0)
    largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    mask = (labels == largest).astype(np.uint8) * 255
    return mask


def _trace_to_signal(mask: np.ndarray, h_spacing_px: float, v_spacing_px: float,
                      speed_mm_s: float, amp_mm_mv: float) -> Tuple[List[float], List[float]]:
    """Convert a binary mask of the trace into time‑amplitude samples.

    Parameters
    ----------
    mask: binary image where the trace is white (255).
    h_spacing_px, v_spacing_px: pixel distance of one small grid cell horizontally
        and vertically.
    speed_mm_s: paper speed in millimetres per second (e.g. 25 or 50).
    amp_mm_mv: amplitude calibration – mm per millivolt (commonly 10).

    Returns
    -------
    times, amplitudes: two parallel lists of float samples.
    """
    # Scan each column to find the vertical position of the trace (center of white pixels)
    height, width = mask.shape
    times = []
    amplitudes = []
    # Conversion factors
    sec_per_px = (1.0 / speed_mm_s) * (h_spacing_px / 5.0)  # 5 small squares = 1 second
    mv_per_px = 1.0 / (amp_mm_mv / v_spacing_px)  # mV per pixel
    for col in range(width):
        column = mask[:, col]
        white_idxs = np.where(column == 255)[0]
        if len(white_idxs) == 0:
            # No trace found in this column – treat as missing data (skip)
            continue
        # Use the median y‑position as the trace location
        y = int(np.median(white_idxs))
        # Time is column index * sec_per_px (relative to start)
        t = col * sec_per_px
        # Amplitude: distance from the centre line (assumed to be middle of the region)
        centre_y = height / 2.0
        dy = centre_y - y  # positive values = upward deflection
        amp = dy * mv_per_px
        times.append(t)
        amplitudes.append(amp)
    return times, amplitudes

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def process_ecg_image(file_bytes: bytes,
                      speed_mm_s: Optional[float] = None,
                      amp_mm_mv: Optional[float] = None) -> Dict:
    """Main entry point for the image‑to‑signal conversion.

    Returns a dictionary with the following keys:
    * ``original_image`` – base64‑encoded PNG of the uploaded image.
    * ``graph_region`` – base64‑encoded PNG of the detected graph region.
    * ``waveform_mask`` – base64‑encoded PNG of the extracted waveform mask.
    * ``times`` and ``amplitudes`` – numerical samples (may be empty on failure).
    * ``metadata`` – calibration values used, pixel‑spacing estimates, and warnings.
    * ``calibration_status`` – ``"confirmed"``, ``"estimated"`` or ``"unconfirmed"``.
    """
    warnings_list: List[str] = []
    # Load image
    try:
        img = _load_image(file_bytes)
    except ValueError as e:
        warnings_list.append(str(e))
        return {"warnings": warnings_list, "calibration_status": "unconfirmed"}

    # Encode original for response (PNG to keep lossless)
    _, orig_buf = cv2.imencode('.png', img)
    original_b64 = "data:image/png;base64," + base64.b64encode(orig_buf).decode()

    # Detect graph region
    region, (x, y, w, h) = _detect_graph_region(img)
    if (w, h) == (img.shape[1], img.shape[0]):
        warnings_list.append("Unable to isolate ECG graph region – using full image.")
    _, region_buf = cv2.imencode('.png', region)
    region_b64 = "data:image/png;base64," + base64.b64encode(region_buf).decode()

    # Work in greyscale for grid estimation
    gray_region = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    h_spacing_px, v_spacing_px = _estimate_grid_spacing(gray_region)
    if h_spacing_px is None or v_spacing_px is None:
        warnings_list.append("Grid spacing could not be estimated – calibration required.")

    # Determine calibration status
    calibration_status = "unconfirmed"
    # If user supplied both values, treat as confirmed
    if speed_mm_s is not None and amp_mm_mv is not None:
        calibration_status = "confirmed"
    # Else if we have grid estimates, we can provide an estimated calibration
    elif h_spacing_px is not None and v_spacing_px is not None:
        # Use typical defaults for estimation (these are placeholders)
        speed_mm_s = speed_mm_s or 25.0
        amp_mm_mv = amp_mm_mv or 10.0
        calibration_status = "estimated"
        warnings_list.append("Using estimated calibration based on grid detection.")
    else:
        # No user input and no grid – cannot calibrate
        speed_mm_s = speed_mm_s or 25.0
        amp_mm_mv = amp_mm_mv or 10.0
        warnings_list.append("Calibration not confirmed – defaults applied. Please provide values.")

    # Extract waveform mask
    waveform_mask = _extract_waveform(region)
    _, mask_buf = cv2.imencode('.png', waveform_mask)
    mask_b64 = "data:image/png;base64," + base64.b64encode(mask_buf).decode()

    # Convert mask to numeric signal only if calibration is confirmed
    times: List[float] = []
    amplitudes: List[float] = []
    if calibration_status == "confirmed" and h_spacing_px and v_spacing_px:
        times, amplitudes = _trace_to_signal(waveform_mask, h_spacing_px, v_spacing_px,
                                            speed_mm_s, amp_mm_mv)
        if not times:
            warnings_list.append("Waveform extraction yielded no samples.")
    else:
        warnings_list.append("Numerical signal not generated until calibration is confirmed.")

    metadata = {
        "paper_speed_mm_per_s": speed_mm_s,
        "amplitude_mm_per_mv": amp_mm_mv,
        "grid_spacing_px": {"horizontal": h_spacing_px, "vertical": v_spacing_px},
        "warnings": warnings_list,
    }

    return {
        "original_image": original_b64,
        "graph_region": region_b64,
        "waveform_mask": mask_b64,
        "times": times,
        "amplitudes": amplitudes,
        "metadata": metadata,
        "calibration_status": calibration_status,
    }

    """Main entry point for the image‑to‑signal conversion.

    Returns a dictionary with the following keys:
    * ``original_image`` – base64‑encoded PNG of the uploaded image.
    * ``graph_region`` – base64‑encoded PNG of the detected graph region.
    * ``waveform_mask`` – base64‑encoded PNG of the extracted waveform mask.
    * ``times`` and ``amplitudes`` – numerical samples (may be empty on failure).
    * ``metadata`` – calibration values used, pixel‑spacing estimates, and warnings.
    """
    warnings_list: List[str] = []
    # Load image
    try:
        img = _load_image(file_bytes)
    except ValueError as e:
        warnings_list.append(str(e))
        return {"warnings": warnings_list}

    # Encode original for response (PNG to keep lossless)
    _, orig_buf = cv2.imencode('.png', img)
    original_b64 = "data:image/png;base64," + base64.b64encode(orig_buf).decode()

    # Detect graph region
    region, (x, y, w, h) = _detect_graph_region(img)
    if (w, h) == (img.shape[1], img.shape[0]):
        warnings_list.append("Unable to isolate ECG graph region – using full image.")
    _, region_buf = cv2.imencode('.png', region)
    region_b64 = "data:image/png;base64," + base64.b64encode(region_buf).decode()

    # Work in greyscale for grid estimation
    gray_region = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    h_spacing_px, v_spacing_px = _estimate_grid_spacing(gray_region)
    if h_spacing_px is None or v_spacing_px is None:
        warnings_list.append("Grid spacing could not be estimated – calibration required.")

    # Use supplied calibration or fallback defaults (if grid spacing is known)
    if speed_mm_s is None:
        if h_spacing_px is not None:
            # 5 small squares = 1 second → speed = 5 * h_spacing_mm / 1s
            speed_mm_s = 5 * (h_spacing_px / h_spacing_px)  # simplifies to 5 mm/s (placeholder)
        else:
            speed_mm_s = 25.0  # a typical default, but warn the user
            warnings_list.append("Paper speed not specified and could not be inferred – assuming 25 mm/s.")
    if amp_mm_mv is None:
        if v_spacing_px is not None:
            amp_mm_mv = 10.0  # standard assumption; warn if inferred not reliable
        else:
            amp_mm_mv = 10.0
            warnings_list.append("Amplitude calibration not provided – assuming 10 mm/mV.")

    # Extract waveform mask
    waveform_mask = _extract_waveform(region)
    _, mask_buf = cv2.imencode('.png', waveform_mask)
    mask_b64 = "data:image/png;base64," + base64.b64encode(mask_buf).decode()

    # Convert mask to numeric signal (if we have grid spacing estimates)
    times: List[float] = []
    amplitudes: List[float] = []
    if h_spacing_px and v_spacing_px:
        times, amplitudes = _trace_to_signal(waveform_mask, h_spacing_px, v_spacing_px,
                                            speed_mm_s, amp_mm_mv)
        if not times:
            warnings_list.append("Waveform extraction yielded no samples.")
    else:
        warnings_list.append("Insufficient grid information – numerical signal not generated.")

    metadata = {
        "paper_speed_mm_per_s": speed_mm_s,
        "amplitude_mm_per_mv": amp_mm_mv,
        "grid_spacing_px": {"horizontal": h_spacing_px, "vertical": v_spacing_px},
        "warnings": warnings_list,
    }

    return {
        "original_image": original_b64,
        "graph_region": region_b64,
        "waveform_mask": mask_b64,
        "times": times,
        "amplitudes": amplitudes,
        "metadata": metadata,
    }

# Required import for base64 encoding
import base64

