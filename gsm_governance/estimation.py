"""Estimation scaffold for M_J (Section 3.3.3, Appendix D).

This module exposes the data structures and protocol required by the paper's
four-constraint estimation regime:
    1. Bounded support
    2. Sign priors on nets
    3. Component sparsity (only committed pairs receive nonzero priors)
    4. Symmetry regime

Full Bayesian inference is not implemented here. The module documents the
protocol and provides the containers a Bayesian implementation would require.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
from .config import (
    GSMConfig, DIMENSIONS, CONTESTED_PAIRS,
    SINGLE_COMPONENT_TENSION_PAIRS, SINGLE_COMPONENT_SYNERGY_PAIRS,
)
from .justice import JusticeInteractionMatrix

Pair = Tuple[str, str]

DEFAULT_SIGN_PRIORS: Dict[Pair, str] = {
    **{p: "+" for p in SINGLE_COMPONENT_SYNERGY_PAIRS},
    **{p: "-" for p in SINGLE_COMPONENT_TENSION_PAIRS},
    **{p: "+/-" for p in CONTESTED_PAIRS},
}

DEFAULT_COMPONENT_MASK: Dict[Pair, Tuple[bool, bool]] = {
    **{p: (True, False) for p in SINGLE_COMPONENT_SYNERGY_PAIRS},
    **{p: (False, True) for p in SINGLE_COMPONENT_TENSION_PAIRS},
    **{p: (True, True) for p in CONTESTED_PAIRS},
}


@dataclass
class EstimationSpec:
    """Data structures required for Appendix D estimation."""
    sign_priors: Dict[Pair, str] = field(
        default_factory=lambda: dict(DEFAULT_SIGN_PRIORS))
    component_mask: Dict[Pair, Tuple[bool, bool]] = field(
        default_factory=lambda: dict(DEFAULT_COMPONENT_MASK))
    symmetry: str = "asymmetric"
    m_max: float = 0.30

    def is_committed(self, d: str, e: str) -> bool:
        return (d, e) in self.component_mask

    def prior_components(self, d: str, e: str) -> Tuple[Optional[float], Optional[float]]:
        """Return (m_plus_prior, m_minus_prior). None means 'to be estimated'."""
        if (d, e) not in self.component_mask:
            return (0.0, 0.0)
        has_p, has_m = self.component_mask[(d, e)]
        p = None if has_p else 0.0
        m = None if has_m else 0.0
        return (p, m)

    def net_sign_prior(self, d: str, e: str) -> str:
        return self.sign_priors.get((d, e), "+/-")


def estimate_MJ(panel_data, config: GSMConfig, spec: Optional[EstimationSpec] = None) -> JusticeInteractionMatrix:
    """Estimate M_J from panel data under Appendix D protocol.

    Raises
    ------
    NotImplementedError
        Full Bayesian inference is not implemented in this scaffold. The
        paper's own Section 3.3.3 states that component identification
        requires additional information (natural experiments or
        cross-context designs) that a library cannot manufacture.
    """
    raise NotImplementedError(
        "estimate_MJ is a scaffold. Full Bayesian inference under Appendix D "
        "requires an observation model and identifying variation that this "
        "library does not impose. Use EstimationSpec to specify priors and "
        "the component mask, and implement inference against a downstream "
        "model. See Appendix D.7 of the paper."
    )
