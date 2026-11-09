"""
Composite indices for GSM-J.
"""

from __future__ import annotations

import numpy as np

from gsm_governance.core.parameters import (
    BASE_CAPABILITIES,
    EPS,
    JUSTICE_DIMENSIONS,
)
from gsm_governance.core.state import ExploitationMatrix
from gsm_governance.core.system import MultiLevelGovernance

# ===========================================================================
# Governance Success Index (GSI)
# ===========================================================================

def gsi(governance: MultiLevelGovernance) -> float:
    """
    Governance Success Index — mean across jurisdictions of the mean of the
    five base capabilities. Retained from v0.2.0.
    """
    juris = governance.jurisdictions
    if not juris:
        return 0.0
    total = 0.0
    for j in juris.values():
        caps = [getattr(j.state, k) for k in BASE_CAPABILITIES]
        total += float(np.mean(caps))
    return total / len(juris)


# ===========================================================================
# Human Flourishing Index (HFI)
# ===========================================================================

def hfi(governance: MultiLevelGovernance) -> float:
    """
    Human Flourishing Index — mean across jurisdictions of the arithmetic
    average of base capabilities and aggregate justice. Retained from v0.2.0
    but redefined to include justice.
    """
    juris = governance.jurisdictions
    if not juris:
        return 0.0
    weights = governance.config.justice_weights
    total = 0.0
    for j in juris.values():
        caps = float(np.mean([getattr(j.state, k) for k in BASE_CAPABILITIES]))
        justice = j.state.justice.aggregate(weights)
        total += 0.5 * caps + 0.5 * justice
    return total / len(juris)


# ===========================================================================
# Justice index
# ===========================================================================

def justice_index(governance: MultiLevelGovernance) -> float:
    """Aggregate justice across all jurisdictions."""
    return governance.aggregate_justice()


def justice_floor_violations(
    governance: MultiLevelGovernance,
) -> dict[str, int]:
    """Count violations of the justice floor per dimension."""
    floors = governance.config.justice_floors
    counts = {d: 0 for d in JUSTICE_DIMENSIONS}
    for j in governance.jurisdictions.values():
        for d in JUSTICE_DIMENSIONS:
            if j.state.justice.d[d] + EPS < floors[d]:
                counts[d] += 1
    return counts


def exploitation_index(
    exploitation: ExploitationMatrix,
) -> dict[tuple[str, str], float]:
    """Return E_ij totals keyed by dyad."""
    return {pair: sum(vals.values())
            for pair, vals in exploitation.E.items()}