"""Image loading pipeline that uses the Decorator pattern."""

from __future__ import annotations

import os
from typing import Optional

import cv2
import numpy as np
import rawpy

from .settings import AnalysisOptions


class ImageLoader:
    """Base component for the decorator chain."""

    def load(self, file_path: str) -> np.ndarray:
        raise NotImplementedError


class CvImageLoader(ImageLoader):
    """Loads RAW/JPEG imagery via OpenCV/rawpy."""

    def load(self, file_path: str) -> np.ndarray:
        lower = file_path.lower()
        if lower.endswith((".raw", ".dng", ".nef", ".cr2", ".arw")):
            if not os.path.exists(file_path):
                raise FileNotFoundError(file_path)
            with rawpy.imread(file_path) as raw:
                return raw.postprocess(output_bps=8)
        image_bgr = cv2.imread(file_path)
        if image_bgr is None:
            raise RuntimeError(f"Не удалось загрузить изображение: {file_path}")
        return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)


class ImageLoaderDecorator(ImageLoader):
    """Base decorator that forwards load calls."""

    def __init__(self, inner: ImageLoader):
        self._inner = inner

    def load(self, file_path: str) -> np.ndarray:
        return self._inner.load(file_path)


class ContrastEnhancementLoader(ImageLoaderDecorator):
    """Decorator: applies CLAHE to highlight vegetation gradients."""

    def load(self, file_path: str) -> np.ndarray:
        image = super().load(file_path)
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        merged = cv2.merge((cl, a, b))
        return cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)


class FieldBoundaryFocusLoader(ImageLoaderDecorator):
    """Decorator: dims background pixels outside detected field boundaries."""

    def load(self, file_path: str) -> np.ndarray:
        image = super().load(file_path)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(
            blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        mask = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        mask_norm = mask.astype(np.float32) / 255.0
        background = np.full_like(image, 25, dtype=np.uint8)
        masked = (
            image.astype(np.float32) * mask_norm[..., None]
            + background.astype(np.float32) * (1.0 - mask_norm[..., None])
        )
        return masked.astype(np.uint8)


def build_loader(options: Optional[AnalysisOptions] = None) -> ImageLoader:
    """Factory method for composing the decorator chain based on settings."""

    loader: ImageLoader = CvImageLoader()
    if not options:
        return loader
    if options.enhance_contrast:
        loader = ContrastEnhancementLoader(loader)
    if options.auto_boundaries:
        loader = FieldBoundaryFocusLoader(loader)
    return loader
