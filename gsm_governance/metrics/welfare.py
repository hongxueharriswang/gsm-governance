"""
Welfare functions for GSM-J.

welfare                   — backward-compatible scalar form
welfare_dimension_specific — dimension-specific prioritarian W*
welfare_components        — returns a breakdown of the terms
"""

from __future__ import annotations

import numpy as np

from gsm_governance.core.parameters import JUSTICE_DIMENSIONS, GSMConfig
from gsm_governance.core.system import MultiLevelGovernance

# ===========================================================================
# Dimension-specific prioritarian welfare
# ===========================================================================

def welfare_dimension_specific(
    base_welfare: float,
    governance: MultiLevelGovernance,
    config: GSMConfig,
) -> float:
    """
    W* = W + sum_d gamma_d J_d
           - sum_d delta_d * max(0, J_min_d - J_d)

    Aggregated across all jurisdictions.
    """
    contribution = 0.0
    penalty = 0.0
    for j in governance.jurisdictions.values():
        for d in JUSTICE_DIMENSIONS:
            contribution += config.gamma_dim[d] * j.state.justice.d[d]
            shortfall = max(
                0.0, config.justice_floors[d] - j.state.justice.d[d])
            penalty += config.delta_dim[d] * shortfall
    return float(base_welfare + contribution - penalty)


# ===========================================================================
# Backward-compatible scalar welfare
# ===========================================================================

def welfare(
    governance: MultiLevelGovernance,
    base_welfare: float | None = None,
) -> float:
    """
    Scalar welfare function.  If base_welfare is None, it is computed
    from the mean of base capabilities.
    """
    if base_welfare is None:
        juris = governance.jurisdictions
        if not juris:
            return 0.0
        base_welfare = float(np.mean([
            np.mean([getattr(j.state, k) for k in ("A", "C", "S", "T", "L")])
            for j in juris.values()
        ]))
    return welfare_dimension_specific(
        base_welfare, governance, governance.config)


# ===========================================================================
# Component breakdown
# ===========================================================================

def welfare_components(
    base_welfare: float,
    governance: MultiLevelGovernance,
    config: GSMConfig,
) -> dict[str, float]:
    """Return a breakdown of the welfare terms."""
    contribution = 0.0
    penalty = 0.0
    for j in governance.jurisdictions.values():
        for d in JUSTICE_DIMENSIONS:
            contribution += config.gamma_dim[d] * j.state.justice.d[d]
            shortfall = max(
                0.0, config.justice_floors[d] - j.state.justice.d[d])
            penalty += config.delta_dim[d] * shortfall
    return {
        "base": float(base_welfare),
        "justice_contribution": float(contribution),
        "prioritarian_penalty": float(penalty),
        "W_star": float(base_welfare + contribution - penalty),
    }