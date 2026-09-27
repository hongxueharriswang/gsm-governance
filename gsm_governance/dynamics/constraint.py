"""
Constraint checking for GSM-J.

BoundedNonExploitationConstraint (C1) — retained from v0.2.0.
JusticeConstraintSet — extended constraints C1–C4.
ConstraintChecker — unified interface.
"""

from __future__ import annotations

from gsm_governance.core.parameters import (
    EPS,
    JUSTICE_DIMENSIONS,
    C4Mode,
    GSMConfig,
)
from gsm_governance.core.state import (
    CompensationMechanism,
    ExploitationMatrix,
)

# ===========================================================================
# C1 — retained from v0.2.0
# ===========================================================================

class BoundedNonExploitationConstraint:
    """
    C1: E_ij <= tau_j  OR  Comp_ij >= E_ij.

    Backward-compatible with v0.2.0. The tau argument may be a scalar
    (applied to all j), a dict keyed by jurisdiction id, or a callable.
    """

    def __init__(self, tau=0.0, valuation_vectors=None) -> None:
        self.tau = tau
        self.valuation_vectors = valuation_vectors or {}

    def _tau_for(self, j: str) -> float:
        if callable(self.tau):
            return float(self.tau(j))
        if isinstance(self.tau, dict):
            return float(self.tau.get(j, 0.0))
        return float(self.tau)

    def _value(self, j: str, comp: dict[str, float]) -> float:
        lam = self.valuation_vectors.get(j)
        if lam is None:
            return float(sum(comp.values()))
        return float(sum(lam.get(d, 1.0) * comp[d]
                         for d in JUSTICE_DIMENSIONS))

    def violated_pairs(
        self,
        exploitation: ExploitationMatrix,
        compensation: CompensationMechanism,
    ) -> list[tuple[str, str]]:
        violations = []
        for (i, j) in exploitation.pairs():
            e_tot = exploitation.total(i, j)
            if e_tot <= self._tau_for(j) + EPS:
                continue
            v = self._value(j, compensation.get(i, j))
            if v + EPS < e_tot:
                violations.append((i, j))
        return violations

    def satisfied(
        self,
        exploitation: ExploitationMatrix,
        compensation: CompensationMechanism,
    ) -> bool:
        return not self.violated_pairs(exploitation, compensation)


# ===========================================================================
# Extended constraints C1–C4
# ===========================================================================

class JusticeConstraintSet:
    """
    Full set of GSM-J constraints:
        C1: bounded non-exploitation
        C2: justice floor (dimension-specific)
        C3: vulnerability-sensitive non-exploitation
        C4: vertical justice alignment (subsidiarity)
    """

    def __init__(self, config: GSMConfig) -> None:
        self.config = config

    # -- C1 ----------------------------------------------------------------

    def C1(self, exploitation, compensation) -> list[tuple[str, str]]:
        c1 = BoundedNonExploitationConstraint(tau=self.config.tau)
        return c1.violated_pairs(exploitation, compensation)

    # -- C2 ----------------------------------------------------------------

    def C2(self, jurisdictions) -> list[tuple[str, str]]:
        """Return list of (uid, dimension) violations of the justice floor."""
        out = []
        for uid, j in jurisdictions.items():
            for d in JUSTICE_DIMENSIONS:
                if j.state.justice.d[d] + EPS < self.config.justice_floors[d]:
                    out.append((uid, d))
        return out

    # -- C3 ----------------------------------------------------------------

    def C3(self, exploitation, jurisdictions) -> list[tuple[str, str]]:
        """Vulnerability-sensitive non-exploitation violations."""
        out = []
        for (i, j) in exploitation.pairs():
            if exploitation.total(i, j) <= EPS:
                continue
            if j not in jurisdictions:
                continue
            agg_j = jurisdictions[j].state.justice.aggregate(
                self.config.justice_weights)
            if agg_j + EPS < self.config.aggregate_floor:
                out.append((i, j))
        return out

    # -- C4 ----------------------------------------------------------------

    def C4(self, jurisdictions) -> list[tuple[str, str]]:
        """Vertical alignment violations (per-dimension by default)."""
        out = []
        mode = self.config.c4_mode
        phi = self.config.phi
        for uid, j in jurisdictions.items():
            if not j.parent or j.parent not in jurisdictions:
                continue
            p = jurisdictions[j.parent]
            if mode in (C4Mode.PER_DIMENSION, C4Mode.HYBRID):
                for d in JUSTICE_DIMENSIONS:
                    target = phi * p.state.justice.d[d]
                    if j.state.justice.d[d] + EPS < target:
                        out.append((uid, d))
            if mode in (C4Mode.AGGREGATE, C4Mode.HYBRID):
                agg_j = j.state.justice.aggregate(self.config.justice_weights)
                agg_p = p.state.justice.aggregate(self.config.justice_weights)
                if agg_j + EPS < phi * agg_p:
                    out.append((uid, "aggregate"))
        return out


# ===========================================================================
# Unified checker
# ===========================================================================

class ConstraintChecker:
    """
    Unified interface for checking all four constraints.

    Usage:
        checker = ConstraintChecker(config)
        violations = {
            "C1": checker.C1(exploitation, compensation),
            "C2": checker.C2(jurisdictions),
            "C3": checker.C3(exploitation, jurisdictions),
            "C4": checker.C4(jurisdictions),
        }
    """

    def __init__(self, config: GSMConfig) -> None:
        self.config = config
        self._set = JusticeConstraintSet(config)
        self._c1 = BoundedNonExploitationConstraint(tau=config.tau)

    def C1(self, exploitation, compensation):
        return self._set.C1(exploitation, compensation)

    def C2(self, jurisdictions):
        return self._set.C2(jurisdictions)

    def C3(self, exploitation, jurisdictions):
        return self._set.C3(exploitation, jurisdictions)

    def C4(self, jurisdictions):
        return self._set.C4(jurisdictions)

    def all(self, exploitation, compensation, jurisdictions) -> dict[str, list]:
        return {
            "C1": self.C1(exploitation, compensation),
            "C2": self.C2(jurisdictions),
            "C3": self.C3(exploitation, jurisdictions),
            "C4": self.C4(jurisdictions),
        }