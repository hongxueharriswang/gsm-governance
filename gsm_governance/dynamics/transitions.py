"""
State transition functions for GSM-J.

justice_step                                 — advance one jurisdiction's justice
base_capability_step                         — advance base capabilities
update_accountability_dimension_specific     — cross-level accountability
"""

from __future__ import annotations

import numpy as np

from gsm_governance.core.parameters import (
    BASE_CAPABILITIES,
    JUSTICE_DIMENSIONS,
    GSMConfig,
    JusticeInteractionMatrix,
)
from gsm_governance.core.state import (
    CompensationMechanism,
    ExploitationMatrix,
)
from gsm_governance.core.system import Jurisdiction, MultiLevelGovernance

# ===========================================================================
# Justice dynamics
# ===========================================================================

def justice_step(
    j: Jurisdiction,
    governance: MultiLevelGovernance,
    exploitation: ExploitationMatrix,
    compensation: CompensationMechanism,
    config: GSMConfig,
    M_J: JusticeInteractionMatrix,
    dt: float,
) -> None:
    """Advance one jurisdiction's justice state by dt (manuscript §4.2)."""
    state = j.state
    A = state.A
    C = state.C
    S = state.S
    T = state.T
    L = state.L
    J = state.justice.d

    # Internal coupling g_d
    g = {
        "distributive":      config.alpha_d["distributive"]      * A * C,
        "procedural":        config.alpha_d["procedural"]        * A * L,
        "recognition":       config.alpha_d["recognition"]       * S * A,
        "corrective":        config.alpha_d["corrective"]        * A,
        "intergenerational": config.alpha_d["intergenerational"] * T * L,
    }

    # Erosion and restoration
    erosion = {d: 0.0 for d in JUSTICE_DIMENSIONS}
    restoration = {d: 0.0 for d in JUSTICE_DIMENSIONS}
    for (i, jj) in exploitation.pairs():
        if jj == j.uid:
            for d in JUSTICE_DIMENSIONS:
                erosion[d] += exploitation.E[(i, jj)][d]
    for (i, jj) in compensation.pairs():
        if jj == j.uid:
            for d in JUSTICE_DIMENSIONS:
                restoration[d] += compensation.C[(i, jj)][d]

    h = {}
    for d in JUSTICE_DIMENSIONS:
        h[d] = (-config.beta_erosion[d] * erosion[d]
                + config.beta_compensation[d] * restoration[d])

    # Corrective restorative coupling
    for (i, jj) in exploitation.pairs():
        if jj == j.uid and (i, jj) in compensation.C:
            for d in JUSTICE_DIMENSIONS:
                h["corrective"] += (
                    config.alpha_corrective_restorative
                    * exploitation.E[(i, jj)][d]
                    * compensation.C[(i, jj)][d]
                )

    # Horizontal diffusion
    diffusion = {d: 0.0 for d in JUSTICE_DIMENSIONS}
    if j.neighbours:
        for d in JUSTICE_DIMENSIONS:
            vals = [
                governance.jurisdictions[nb].state.justice.d[d]
                for nb in j.neighbours if nb in governance.jurisdictions
            ]
            if vals:
                diffusion[d] = config.eta * (float(np.mean(vals)) - J[d])

    # Coupling matrix
    coupling = {d: M_J.coupling(J, d) for d in JUSTICE_DIMENSIONS}

    # Update
    for d in JUSTICE_DIMENSIONS:
        dJ = (g[d] + h[d] + coupling[d] + diffusion[d]
              - config.kappa_d[d] * J[d])
        new_val = float(np.clip(J[d] + dt * dJ, 0.0, 1.0))
        state.justice.d[d] = new_val


# ===========================================================================
# Base capability dynamics
# ===========================================================================

def base_capability_step(
    j: Jurisdiction,
    governance: MultiLevelGovernance,
    config: GSMConfig,
    dt: float,
) -> None:
    """
    Each base capability drifts toward a target determined by the
    jurisdiction's justice profile (and, for accountability, the worst-off
    child's aggregate justice).
    """
    state = j.state
    juris = governance.jurisdictions

    child_ids = [c for c in j.children if c in juris]
    if child_ids:
        a_target = min(
            juris[c].state.justice.aggregate(config.justice_weights)
            for c in child_ids
        )
    else:
        a_target = state.A

    targets = {
        "A": a_target,
        "C": 0.5 + 0.3 * (state.justice.d["distributive"] - 0.5),
        "S": 0.5 + 0.3 * (state.justice.d["recognition"] - 0.5),
        "T": 0.5 + 0.3 * (state.justice.d["intergenerational"] - 0.5),
        "L": 0.5 + 0.3 * (state.justice.d["procedural"] - 0.5),
    }

    for k in BASE_CAPABILITIES:
        coupling = config.capability_coupling[k] * (targets[k] - getattr(state, k))
        new_val = float(np.clip(getattr(state, k) + dt * coupling, 0.0, 1.0))
        setattr(state, k, new_val)


# ===========================================================================
# Dimension-specific accountability
# ===========================================================================

def update_accountability_dimension_specific(
    parent: Jurisdiction,
    governance: MultiLevelGovernance,
    config: GSMConfig,
) -> None:
    """
    Dimension-specific cross-level accountability (manuscript §4.3).

    A_parent <- A_parent + lam_c * (m_avg - A_parent)
              - sum_d lambda_p_d * [J_min_d - m_d]^+

    where m_d = min over children of justice dimension d.
    """
    if not parent.children:
        return
    juris = governance.jurisdictions
    child_ids = [c for c in parent.children if c in juris]
    if not child_ids:
        return

    m_dim = {}
    for d in JUSTICE_DIMENSIONS:
        m_dim[d] = min(
            juris[c].state.justice.d[d] for c in child_ids
        )
    m_avg = float(np.mean(list(m_dim.values())))

    coupling = config.lam_c * (m_avg - parent.state.A)
    penalty = 0.0
    for d in JUSTICE_DIMENSIONS:
        shortfall = max(0.0, config.justice_floors[d] - m_dim[d])
        penalty += config.lambda_p_dim[d] * shortfall

    parent.state.A = float(np.clip(
        parent.state.A + coupling - penalty, 0.0, 1.0))