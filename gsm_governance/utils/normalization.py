"""Normalization utilities."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def min_max_normalize(
    values: Iterable[float],
    lo: float | None = None,
    hi: float | None = None,
) -> np.ndarray:
    """Min-max normalize an iterable to [0, 1]."""
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return arr
    lo = arr.min() if lo is None else lo
    hi = arr.max() if hi is None else hi
    if hi - lo < 1e-12:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def z_score_normalize(values: Iterable[float]) -> np.ndarray:
    """Z-score normalize an iterable."""
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return arr
    mu = arr.mean()
    sigma = arr.std()
    if sigma < 1e-12:
        return np.zeros_like(arr)
    return (arr - mu) / sigma