"""Justice interaction matrix M_J with explicit component decomposition.

The matrix is decomposed (Section 3.3.2) into a non-negative synergy
component and a non-positive tension component:
    M_J = M_J^(+) + M_J^(-), m_de = m_de^+ + m_de^-
"""
from dataclasses import dataclass, field
from typing import Dict, Tuple
from .config import (
    DIMENSIONS, CONTESTED_PAIRS, SINGLE_COMPONENT_TENSION_PAIRS,
    SINGLE_COMPONENT_SYNERGY_PAIRS,
)

Pair = Tuple[str, str]


def _default_m_plus() -> Dict[Pair, float]:
    """Illustrative synergy priors (Section 3.3.2, Table 4)."""
    return {
        ("procedural", "recognition"): 0.08,
        ("recognition", "procedural"): 0.08,
        ("distributive", "procedural"): 0.06,
        ("procedural", "distributive"): 0.06,
        ("distributive", "corrective"): 0.05,
        ("corrective", "recognition"): 0.05,
        ("recognition", "corrective"): 0.05,
        ("intergenerational", "procedural"): 0.10,
    }


def _default_m_minus() -> Dict[Pair, float]:
    """Illustrative tension priors (Section 3.3.2, Table 5). Values negative."""
    return {
        ("intergenerational", "distributive"): -0.06,
        ("distributive", "intergenerational"): -0.06,
        ("corrective", "distributive"): -0.04,
        ("procedural", "intergenerational"): -0.05,
        ("intergenerational", "procedural"): -0.05,
    }


@dataclass
class JusticeInteractionMatrix:
    """Signed interaction matrix with component decomposition.

    Component bounds (Section 3.3.2):
        0 <= m_plus[d,e] <= m_max
        -m_max <= m_minus[d,e] <= 0
        |m_plus[d,e] + m_minus[d,e]| <= m_max
    """
    m_max: float = 0.30
    symmetry: str = "asymmetric"
    m_plus: Dict[Pair, float] = field(default_factory=_default_m_plus)
    m_minus: Dict[Pair, float] = field(default_factory=_default_m_minus)

    def __post_init__(self):
        self._validate()
        if self.symmetry == "symmetric":
            self._symmetrize()

    def _validate(self):
        for (d, e), v in self.m_plus.items():
            if d not in DIMENSIONS or e not in DIMENSIONS:
                raise ValueError(f"invalid pair ({d}, {e})")
            if v < 0 or v > self.m_max + 1e-9:
                raise ValueError(f"m_plus[{d},{e}]={v} out of [0, {self.m_max}]")
        for (d, e), v in self.m_minus.items():
            if d not in DIMENSIONS or e not in DIMENSIONS:
                raise ValueError(f"invalid pair ({d}, {e})")
            if v > 0 or v < -self.m_max - 1e-9:
                raise ValueError(f"m_minus[{d},{e}]={v} out of [-{self.m_max}, 0]")
        for pair in set(self.m_plus) | set(self.m_minus):
            net = self.m_plus.get(pair, 0.0) + self.m_minus.get(pair, 0.0)
            if abs(net) > self.m_max + 1e-9:
                raise ValueError(f"net {pair}={net} exceeds |m_max|")

    def _symmetrize(self):
        pairs = set(self.m_plus) | set(self.m_minus)
        for (d, e) in pairs:
            if d >= e:
                continue
            rp, rm = (e, d), (d, e)
            p = 0.5 * (self.m_plus.get(rp, 0.0) + self.m_plus.get(rm, 0.0))
            m = 0.5 * (self.m_minus.get(rp, 0.0) + self.m_minus.get(rm, 0.0))
            p = max(0.0, min(self.m_max, p))
            m = min(0.0, max(-self.m_max, m))
            if p > 0:
                self.m_plus[rp] = self.m_plus[rm] = p
            if m < 0:
                self.m_minus[rp] = self.m_minus[rm] = m

    @property
    def m(self) -> Dict[Pair, float]:
        """Net coefficients (Section 3.3.2). Backwards-compatible with 0.3.0."""
        out: Dict[Pair, float] = {}
        for pair in set(self.m_plus) | set(self.m_minus):
            out[pair] = self.m_plus.get(pair, 0.0) + self.m_minus.get(pair, 0.0)
        return out

    def get(self, d: str, e: str) -> float:
        return self.m_plus.get((d, e), 0.0) + self.m_minus.get((d, e), 0.0)

    def pair_type(self, d: str, e: str) -> str:
        pair = (d, e)
        if pair in CONTESTED_PAIRS:
            return "contested"
        if pair in SINGLE_COMPONENT_TENSION_PAIRS:
            return "single_component_tension"
        if pair in SINGLE_COMPONENT_SYNERGY_PAIRS:
            return "single_component_synergy"
        return "uncommitted"

    def coupling(self, justice: Dict[str, float]) -> Dict[str, float]:
        """C_J^d(J_i) = sum_{e != d} (m_de^+ + m_de^-) J^e (1 - J^d)."""
        out = {}
        for d in DIMENSIONS:
            acc = 0.0
            for e in DIMENSIONS:
                if e == d:
                    continue
                coeff = self.get(d, e)
                if coeff == 0.0:
                    continue
                acc += coeff * justice[e] * (1.0 - justice[d])
            out[d] = acc
        return out
