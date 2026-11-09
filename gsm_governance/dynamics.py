"""Justice and capability dynamics (Sections 4.1, 4.2)."""
from typing import Optional
from .config import GSMConfig, DIMENSIONS, CAPABILITIES


def justice_step(
    jurisdiction,
    config: GSMConfig,
    interaction,
    exploitation_by_dim: Optional[dict] = None,
) -> dict:
    """Compute the justice increment (Section 4.1):

    J^{d,l}(t+1) = J^{d,l}(t) + alpha_d * [
        C_J^d(J)                          # endogenous interaction
      + beta_d * (J_parent^d - J^{d,l})   # vertical alignment pressure
      - gamma_d * E_i^d                   # exploitation drag
    ]
    """
    J = jurisdiction.state.justice
    C = interaction.coupling(J)
    E = exploitation_by_dim or {d: 0.0 for d in DIMENSIONS}

    out = {}
    for d in DIMENSIONS:
        alignment = 0.0
        if jurisdiction.parent is not None:
            J_parent = jurisdiction.parent.state.justice[d]
            alignment = config.beta[d] * (J_parent - J[d])
        drag = config.gamma[d] * E.get(d, 0.0)
        out[d] = config.alpha[d] * (C[d] + alignment - drag)
    return out


def capability_step(jurisdiction, config: GSMConfig, deltas: Optional[dict] = None) -> dict:
    """Capability cluster update (Section 4.2)."""
    mean_J = sum(jurisdiction.state.justice.values()) / len(DIMENSIONS)
    deltas = deltas or {}
    out = {}
    for c in CAPABILITIES:
        drift = config.capability_coupling[c] * (mean_J - jurisdiction.state.capabilities[c])
        out[c] = drift + deltas.get(c, 0.0)
    return out
