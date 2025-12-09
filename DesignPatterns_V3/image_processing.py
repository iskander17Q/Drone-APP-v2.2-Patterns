"""Backward compatible wrappers around analysis module helpers."""

from analysis import classify_index, compute_indices, generate_heatmap, load_image

__all__ = [
    "load_image",
    "compute_indices",
    "generate_heatmap",
    "classify_index",
]
