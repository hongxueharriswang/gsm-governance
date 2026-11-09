"""
Configuration parameters for GSM-J.

This module holds:
  * Enumerations (C4Mode, MJRegime, EnforcementMode)
  * The dimension and capability constants
  * GSMConfig: the full parameter set (normative + structural)
  * JusticeInteractionMatrix: the M_J coupling matrix
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np

# ===========================================================================
# Constants
# ===========================================================================

JUSTICE_DIMENSIONS: tuple[str, ...] = (
    "distributive",
    "procedural",
    "recognition",
    "corrective",
    "intergenerational",
)

BASE_CAPABILITIES: tuple[str, ...] = ("A", "C", "S", "T", "L")

INTERVENTION_CHANNELS: tuple[str, ...] = ("C", "S", "T", "A")

EPS: float = 1e-9


# ===========================================================================
# Enumerations
# ===========================================================================

class C4Mode(Enum):
    """Vertical alignment (subsidiarity) constraint formulation."""
    PER_DIMENSION = "per_dimension"
    AGGREGATE = "aggregate"
    HYBRID = "hybrid"


class MJRegime(Enum):
    """Estimation regime for the justice interaction matrix."""
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"


class EnforcementMode(Enum):
    """Constraint enforcement mode (manuscript §6.4)."""
    PROJECTION = "A"
    PENALTY = "B"
    HYBRID = "hybrid"


# ===========================================================================
# GSMConfig
# ===========================================================================

@dataclass
class GSMConfig:
    """
    Full parameter set for a GSM-J simulation.

    Grouped into two conceptually distinct blocks:
      * Structural parameters — describe system dynamics (calibratable)
      * Normative parameters — encode value judgments (must be justified)

    Every study should document the normative parameter choices.
    See manuscript Appendix B for the reporting checklist.
    """

    # ---- structural: hierarchy -------------------------------------------
    n_levels: int = 6
    dt: float = 0.05

    # ---- structural: base capability dynamics ----------------------------
    capability_coupling: dict[str, float] = field(default_factory=lambda: {
        "A": 0.05, "C": 0.05, "S": 0.05, "T": 0.05, "L": 0.05,
    })

    # ---- structural: justice dynamics ------------------------------------
    eta: float = 0.20                                # horizontal diffusion
    kappa_d: dict[str, float] = field(default_factory=lambda: {
        d: 0.05 for d in JUSTICE_DIMENSIONS
    })
    alpha_d: dict[str, float] = field(default_factory=lambda: {
        "distributive":      0.30,
        "procedural":        0.30,
        "recognition":       0.25,
        "corrective":        0.20,
        "intergenerational": 0.35,
    })
    alpha_corrective_restorative: float = 0.30
    beta_erosion: dict[str, float] = field(default_factory=lambda: {
        d: 0.40 for d in JUSTICE_DIMENSIONS
    })
    beta_compensation: dict[str, float] = field(default_factory=lambda: {
        d: 0.50 for d in JUSTICE_DIMENSIONS
    })

    # ---- structural: cross-level accountability --------------------------
    lam_c: float = 0.15

    # ---- structural: justice suppression of exploitation -----------------
    mu: float = 0.25

    # ---- structural: policy intervention ---------------------------------
    intervention_cost: float = 0.10
    intervention_horizon: int = 5
    intervention_weights: dict[str, float] = field(default_factory=lambda: {
        "C": 0.50, "S": 0.25, "T": 0.15, "A": 0.10,
    })
    recovery: dict[str, float] = field(default_factory=lambda: {
        "C": 0.05, "S": 0.05, "T": 0.05, "A": 0.05,
    })
    enforcement_mode: EnforcementMode = EnforcementMode.HYBRID

    # ---- normative: justice weights and floors ---------------------------
    justice_weights: dict[str, float] = field(default_factory=lambda: {
        "distributive": 0.25,
        "procedural": 0.20,
        "recognition": 0.20,
        "corrective": 0.15,
        "intergenerational": 0.20,
    })
    justice_floors: dict[str, float] = field(default_factory=lambda: {
        "distributive": 0.30,
        "procedural": 0.25,
        "recognition": 0.25,
        "corrective": 0.10,
        "intergenerational": 0.20,
    })
    aggregate_floor: float = 0.30

    # ---- normative: welfare coefficients ---------------------------------
    gamma_dim: dict[str, float] | None = None
    delta_dim: dict[str, float] | None = None

    # ---- normative: accountability penalties -----------------------------
    lambda_p_dim: dict[str, float] = field(default_factory=lambda: {
        "distributive": 0.30,
        "procedural": 0.30,
        "recognition": 0.45,
        "corrective": 0.20,
        "intergenerational": 0.35,
    })

    # ---- normative: subsidiarity -----------------------------------------
    phi: float = 0.85
    c4_mode: C4Mode = C4Mode.PER_DIMENSION

    # ---- normative: tolerance thresholds ---------------------------------
    tau: dict[str, float] = field(default_factory=dict)

    # ---- derived (populated in __post_init__) ----------------------------
    def __post_init__(self) -> None:
        if self.gamma_dim is None:
            self.gamma_dim = {
                d: 0.75 * self.justice_weights[d] for d in JUSTICE_DIMENSIONS
            }
        if self.delta_dim is None:
            self.delta_dim = {
                d: 2.0 * self.justice_weights[d] for d in JUSTICE_DIMENSIONS
            }
        self.validate()

    def validate(self) -> None:
        """Raise ValueError if parameters are inconsistent."""
        w_sum = sum(self.justice_weights.values())
        if abs(w_sum - 1.0) > 1e-6:
            raise ValueError(
                f"justice_weights must sum to 1, got {w_sum:.6f}"
            )
        for d in JUSTICE_DIMENSIONS:
            if self.justice_weights[d] < 0:
                raise ValueError(f"weight for {d} must be non-negative")
            if self.justice_floors[d] < 0:
                raise ValueError(f"floor for {d} must be non-negative")
            if self.delta_dim[d] <= self.gamma_dim[d]:
                raise ValueError(
                    f"prioritarian penalty must exceed welfare weight "
                    f"for {d} ({self.delta_dim[d]} <= {self.gamma_dim[d]})"
                )
        iw_sum = sum(self.intervention_weights.values())
        if abs(iw_sum - 1.0) > 1e-6:
            raise ValueError(
                f"intervention_weights must sum to 1, got {iw_sum:.6f}"
            )

    def justify_floor(self, dimension: str, tradition: str) -> str:
        """Return a human-readable justification string for a floor."""
        if tradition not in ("sufficientarian", "capability", "human_rights"):
            raise ValueError(f"unrecognized normative tradition: {tradition}")
        return (
            f"{dimension}={self.justice_floors[dimension]:.3f} "
            f"justified by {tradition} framework"
        )

    @classmethod
    def default_demo(cls) -> GSMConfig:
        """Return the default configuration used in the demonstration."""
        return cls()


# ===========================================================================
# JusticeInteractionMatrix
# ===========================================================================

@dataclass
class JusticeInteractionMatrix:
    """
    Signed matrix M_J capturing synergies and tensions between justice
    dimensions.

    Coupling term for target dimension d:
        C_J^d(J) = sum_{e != d} m_{de} * J_e * (1 - J_d)

    Positive m: synergy.  Negative m: tension.  Bounded by m_max.
    """

    m: dict[tuple[str, str], float] = field(default_factory=lambda: {
        # Synergies
        ("procedural", "recognition"):        +0.15,
        ("recognition", "procedural"):        +0.15,
        ("distributive", "procedural"):       +0.10,
        ("procedural", "distributive"):       +0.10,
        ("distributive", "corrective"):       +0.15,
        ("corrective", "recognition"):        +0.20,
        ("recognition", "corrective"):        +0.15,
        ("intergenerational", "procedural"):  +0.05,
        # Tensions
        ("intergenerational", "distributive"): -0.05,
        ("distributive", "intergenerational"): -0.05,
        ("corrective", "distributive"):        -0.10,
        ("procedural", "intergenerational"):   -0.05,
    })
    m_max: float = 0.30
    regime: MJRegime = MJRegime.SYMMETRIC

    def __post_init__(self) -> None:
        if self.regime == MJRegime.SYMMETRIC:
            self.symmetrize()

    def _clip(self, v: float) -> float:
        return float(np.clip(v, -self.m_max, self.m_max))

    def coupling(self, J: dict[str, float], d: str) -> float:
        """Compute the coupling term for target dimension d."""
        total = 0.0
        for (src, tgt), coef in self.m.items():
            if tgt == d and src in J:
                total += self._clip(coef) * J[src] * (1.0 - J[d])
        return total

    def symmetrize(self) -> None:
        """Average symmetric pairs of coefficients."""
        keys = list(self.m.keys())
        for (src, tgt) in keys:
            if (tgt, src) in self.m:
                avg = (self.m[(src, tgt)] + self.m[(tgt, src)]) / 2.0
                self.m[(src, tgt)] = avg
                self.m[(tgt, src)] = avg

    def copy(self) -> JusticeInteractionMatrix:
        return JusticeInteractionMatrix(
            m=dict(self.m), m_max=self.m_max, regime=self.regime
        )