"""
Misalignment metrics: divergence between jurisdictional justice profiles
and their parents or peers.
"""

from __future__ import annotations

import numpy as np

from gsm_governance.core.parameters import JUSTICE_DIMENSIONS
from gsm_governance.core.system import MultiLevelGovernance


def misalignment(governance: MultiLevelGovernance) -> float:
    """
    Aggregate vertical misalignment: mean L1 distance between each
    jurisdiction's aggregate justice and its parent's.
    """
    juris = governance.jurisdictions
    weights = governance.config.justice_weights
    diffs = []
    for j in juris.values():
        if not j.parent or j.parent not in juris:
            continue
        p = juris[j.parent]
        diffs.append(abs(
            j.state.justice.aggregate(weights)
            - p.state.justice.aggregate(weights)
        ))
    return float(np.mean(diffs)) if diffs else 0.0


def justice_misalignment(
    governance: MultiLevelGovernance,
) -> dict[str, float]:
    """Per-dimension vertical misalignment."""
    juris = governance.jurisdictions
    acc = {d: [] for d in JUSTICE_DIMENSIONS}
    for j in juris.values():
        if not j.parent or j.parent not in juris:
            continue
        p = juris[j.parent]
        for d in JUSTICE_DIMENSIONS:
            acc[d].append(abs(j.state.justice.d[d] - p.state.justice.d[d]))
    return {d: float(np.mean(v)) if v else 0.0 for d, v in acc.items()}