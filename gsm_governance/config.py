"""Configuration for the GSM-J simulation.

Every normative parameter exposed in Section 7.2 of the theory appears here
as an explicit, settable field. The defaults are illustrative only.
"""
from dataclasses import dataclass, field
from typing import Optional

DIMENSIONS = ("distributive", "procedural", "recognition", "corrective", "intergenerational")
CAPABILITIES = ("accountability", "competence", "cohesion", "continuity", "learning")

# Section 3.3.2: pairs on which the theory makes component commitments.
# A contested pair carries both components; single-component pairs carry one
# component with the other fixed at zero.
CONTESTED_PAIRS = frozenset({("intergenerational", "procedural")})

SINGLE_COMPONENT_TENSION_PAIRS = frozenset({
    ("intergenerational", "distributive"),
    ("distributive", "intergenerational"),
    ("corrective", "distributive"),
    ("procedural", "intergenerational"),
})

SINGLE_COMPONENT_SYNERGY_PAIRS = frozenset({
    ("procedural", "recognition"),
    ("recognition", "procedural"),
    ("distributive", "procedural"),
    ("procedural", "distributive"),
    ("distributive", "corrective"),
    ("corrective", "recognition"),
    ("recognition", "corrective"),
})

# Seven synergy pairs + four tension pairs + one contested pair = twelve
# committed ordered pairs; the remaining eight off-diagonal pairs carry no
# specified component and their priors are zero (Section 3.3.2).


@dataclass
class GSMConfig:
    """Configuration for GSM-J.

    All normative parameters are exposed and swappable (Section 1.7).
    Changing any of them produces a different model whose consequences are
    inspectable.
    """

    # --- Dynamics (Section 4.1) ---
    alpha: dict = field(default_factory=lambda: {d: 0.10 for d in DIMENSIONS})
    beta: dict = field(default_factory=lambda: {d: 0.08 for d in DIMENSIONS})
    gamma: dict = field(default_factory=lambda: {d: 0.05 for d in DIMENSIONS})

    # --- Welfare (Section 4.3) ---
    gamma_w: dict = field(default_factory=lambda: {d: 1.00 for d in DIMENSIONS})
    delta_w: dict = field(default_factory=lambda: {d: 0.50 for d in DIMENSIONS})
    weights: dict = field(default_factory=lambda: {d: 0.20 for d in DIMENSIONS})
    welfare_mode: str = "quadratic"  # or "linear_floor"

    # --- Floors and thresholds (Section 3.6) ---
    floors: dict = field(default_factory=lambda: {
        "distributive": 0.30, "procedural": 0.25, "recognition": 0.25,
        "corrective": 0.10, "intergenerational": 0.20,
    })
    aggregate_floor: float = 0.22
    default_tau: float = 0.05

    # --- Constraint parameters ---
    phi_vuln: float = 0.50
    phi_d: dict = field(default_factory=lambda: {d: 0.05 for d in DIMENSIONS})
    lambda_pd: dict = field(default_factory=lambda: {d: 0.05 for d in DIMENSIONS})

    # --- Interaction matrix (Section 3.3.2) ---
    m_max: float = 0.30
    symmetry: str = "asymmetric"  # or "symmetric"

    # --- Capability coupling (Section 4.2) ---
    capability_coupling: dict = field(default_factory=lambda: {c: 0.02 for c in CAPABILITIES})

    # --- Intervention (Section 4.1) ---
    kappa_int: float = 0.10
    tau_int: int = 5
    omega_k: dict = field(default_factory=lambda: {
        "fiscal": 0.20, "infra": 0.20, "representational": 0.20,
        "regulatory": 0.20, "future": 0.10, "restitution": 0.10,
    })
    recovery_rate: float = 0.02

    # --- Numerics ---
    epsilon: float = 1e-9
    seed: Optional[int] = None

    def __post_init__(self):
        s = sum(self.weights.values())
        if abs(s - 1.0) > 1e-6:
            raise ValueError(f"weights must sum to 1, got {s}")
        for d in DIMENSIONS:
            if self.phi_d[d] < 0:
                raise ValueError("phi_d must be non-negative (absolute margin)")
            if self.gamma_w[d] <= 0:
                raise ValueError("gamma_w must be positive")
            if self.delta_w[d] < 0:
                raise ValueError("delta_w must be non-negative")
        if not (0.0 <= self.phi_vuln <= 1.0):
            raise ValueError("phi_vuln must be in [0, 1]")
        if self.welfare_mode not in ("quadratic", "linear_floor"):
            raise ValueError("welfare_mode must be 'quadratic' or 'linear_floor'")
        if self.symmetry not in ("symmetric", "asymmetric"):
            raise ValueError("symmetry must be 'symmetric' or 'asymmetric'")
