from __future__ import annotations

"""Utilities for loading and validating images before they enter the pipeline.

This module keeps the preprocessing step intentionally simple for the educational
prototype. It is the right place to add DICOM handling, windowing or quality
checks in a more advanced version.
"""

from pathlib import Path
from PIL import Image

ALLOWED_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp"}

def load_image(path: str | Path, size: tuple[int, int] = (512, 512)) -> Image.Image:
    """Load an image safely for the educational prototype.

    This function intentionally keeps preprocessing minimal. For real CXR work,
    DICOM metadata, windowing, projection and acquisition details should be handled
    explicitly and documented.
    """
    path = Path(path)
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError(f"Unsupported image format: {path.suffix}")
    img = Image.open(path).convert("RGB")
    return img.resize(size)

def basic_quality_flag(path: str | Path) -> str:
    """Toy quality flag based on filename metadata.

    Replace this with real image-quality checks in a serious implementation.
    """
    name = Path(path).name.lower()
    if "uncertain" in name or "limited" in name:
        return "limited"
    return "good"