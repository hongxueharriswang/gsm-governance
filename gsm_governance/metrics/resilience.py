"""
Resilience metrics: recovery rate after shocks.
"""

from __future__ import annotations

import numpy as np


def resilience(history: list[dict], shock_time: float) -> float:
    """
    Resilience = ratio of post-shock recovery slope to pre-shock slope
    for welfare W*.  Returns a value in [0, 1+] (clipped at 0 if
    welfare continues to fall).
    """
    if len(history) < 10:
        return 0.0

    times = np.array([r["t"] for r in history])
    w = np.array([r["W_star"] for r in history])

    pre = times < shock_time
    post = times >= shock_time
    if pre.sum() < 3 or post.sum() < 3:
        return 0.0

    pre_slope = np.polyfit(times[pre], w[pre], 1)[0]
    post_slope = np.polyfit(times[post], w[post], 1)[0]

    if pre_slope <= 0:
        return 0.0
    return float(max(0.0, post_slope / pre_slope))