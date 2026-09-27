"""
State representations for GSM-J.

JusticeState       — five-dimensional justice capability
GovernanceState    — full state vector (five capabilities + justice)
FlourishingState   — base flourishing indicators
CompensationVector — the six-component compensation vector
ExploitationMatrix — E_ij decomposed by justice dimension
CompensationMechanism — Comp_ij mapped to justice dimensions
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

import numpy as np

from gsm_governance.core.parameters import (
    BASE_CAPABILITIES,
    EPS,
    JUSTICE_DIMENSIONS,
)

# ===========================================================================
# JusticeState
# ===========================================================================

class JusticeState:
    """Five-dimensional justice capability for a single jurisdiction."""

    __slots__ = ("d",)

    def __init__(self, values: dict[str, float] | None = None):
        src = values or {}
        self.d: dict[str, float] = {
            k: float(np.clip(src.get(k, 0.5), 0.0, 1.0))
            for k in JUSTICE_DIMENSIONS
        }

    def aggregate(self, weights: dict[str, float]) -> float:
        return float(sum(weights[d] * self.d[d] for d in JUSTICE_DIMENSIONS))

    def satisfies_floors(self, floors: dict[str, float]) -> bool:
        return all(self.d[d] >= floors[d] - EPS for d in JUSTICE_DIMENSIONS)

    def floor_deficits(self, floors: dict[str, float]) -> dict[str, float]:
        return {d: max(0.0, floors[d] - self.d[d]) for d in JUSTICE_DIMENSIONS}

    def copy(self) -> JusticeState:
        return JusticeState(dict(self.d))

    def as_dict(self) -> dict[str, float]:
        return dict(self.d)

    def __getitem__(self, key: str) -> float:
        return self.d[key]

    def __setitem__(self, key: str, value: float) -> None:
        if key not in self.d:
            raise KeyError(f"unknown justice dimension: {key}")
        self.d[key] = float(np.clip(value, 0.0, 1.0))

    def __repr__(self) -> str:
        inner = ", ".join(f"{d[:4]}={self.d[d]:.2f}" for d in JUSTICE_DIMENSIONS)
        return f"JusticeState({inner})"


# ===========================================================================
# GovernanceState
# ===========================================================================

@dataclass
class GovernanceState:
    """
    Full state vector for a jurisdiction:
        [A, C, S, T, L] + J

    A/C/S/T/L are scalar capabilities in [0, 1].  J is a JusticeState.
    """

    A: float = 0.5   # accountability
    C: float = 0.5   # institutional competence
    S: float = 0.5   # social cohesion
    T: float = 0.5   # strategic continuity
    L: float = 0.5   # adaptive learning
    justice: JusticeState = field(default_factory=JusticeState)

    def __post_init__(self) -> None:
        for k in ("A", "C", "S", "T", "L"):
            v = getattr(self, k)
            setattr(self, k, float(np.clip(v, 0.0, 1.0)))
        if isinstance(self.justice, dict):
            self.justice = JusticeState(self.justice)

    def capabilities(self) -> dict[str, float]:
        return {k: getattr(self, k) for k in BASE_CAPABILITIES}

    def set_capability(self, key: str, value: float) -> None:
        if key not in BASE_CAPABILITIES:
            raise KeyError(f"unknown capability: {key}")
        setattr(self, key, float(np.clip(value, 0.0, 1.0)))

    def copy(self) -> GovernanceState:
        return GovernanceState(
            A=self.A, C=self.C, S=self.S, T=self.T, L=self.L,
            justice=self.justice.copy(),
        )

    def as_dict(self) -> dict:
        return {
            "capabilities": self.capabilities(),
            "justice": self.justice.as_dict(),
        }


# ===========================================================================
# FlourishingState
# ===========================================================================

@dataclass
class FlourishingState:
    """
    Base flourishing indicators.  Retained for compatibility with v0.2.0.
    """

    wellbeing: float = 0.5
    health: float = 0.5
    meaning: float = 0.5
    relationships: float = 0.5
    autonomy: float = 0.5

    def aggregate(self) -> float:
        return float(np.mean([
            self.wellbeing, self.health, self.meaning,
            self.relationships, self.autonomy,
        ]))


# ===========================================================================
# CompensationVector
# ===========================================================================

@dataclass
class CompensationVector:
    """
    Six-component compensation vector transferred from i to j.

    Components map onto justice dimensions:
        fiscal -> J^D
        infrastructural -> J^D, J^C
        representational -> J^P, J^R
        regulatory -> J^P, J^R, J^I
        future_oriented -> J^I
        restitutional -> J^C
    """

    fiscal: float = 0.0
    infrastructural: float = 0.0
    representational: float = 0.0
    regulatory: float = 0.0
    future_oriented: float = 0.0
    restitutional: float = 0.0

    def total(self) -> float:
        return float(
            self.fiscal + self.infrastructural + self.representational
            + self.regulatory + self.future_oriented + self.restitutional
        )

    def to_justice_dimensions(self) -> dict[str, float]:
        """Distribute compensation across justice dimensions."""
        return {
            "distributive": (
                0.6 * self.fiscal
                + 0.4 * self.infrastructural
            ),
            "procedural": (
                0.5 * self.representational
                + 0.5 * self.regulatory
            ),
            "recognition": (
                0.5 * self.representational
                + 0.5 * self.regulatory
            ),
            "corrective": (
                0.4 * self.infrastructural
                + 1.0 * self.restitutional
            ),
            "intergenerational": (
                0.5 * self.regulatory
                + 1.0 * self.future_oriented
            ),
        }


# ===========================================================================
# ExploitationMatrix
# ===========================================================================

class ExploitationMatrix:
    """Tracks E_ij(t) decomposed by justice dimension."""

    def __init__(self) -> None:
        self.E: dict[tuple[str, str], dict[str, float]] = {}

    def get(self, i: str, j: str) -> dict[str, float]:
        if (i, j) not in self.E:
            self.E[(i, j)] = {d: 0.0 for d in JUSTICE_DIMENSIONS}
        return self.E[(i, j)]

    def total(self, i: str, j: str) -> float:
        return float(sum(self.get(i, j).values()))

    def set(self, i: str, j: str, values: dict[str, float]) -> None:
        self.E[(i, j)] = {
            d: max(0.0, float(values.get(d, 0.0)))
            for d in JUSTICE_DIMENSIONS
        }

    def reduce(self, i: str, j: str, amount: float) -> None:
        if (i, j) not in self.E:
            return
        per_dim = amount / len(JUSTICE_DIMENSIONS)
        self.E[(i, j)] = {
            d: max(0.0, v - per_dim)
            for d, v in self.E[(i, j)].items()
        }

    def pairs(self) -> Iterable[tuple[str, str]]:
        return list(self.E.keys())

    def copy(self) -> ExploitationMatrix:
        new = ExploitationMatrix()
        new.E = {k: dict(v) for k, v in self.E.items()}
        return new


# ===========================================================================
# CompensationMechanism
# ===========================================================================

class CompensationMechanism:
    """Tracks Comp_ij(t) mapped to justice dimensions."""

    def __init__(self) -> None:
        self.C: dict[tuple[str, str], dict[str, float]] = {}

    def get(self, i: str, j: str) -> dict[str, float]:
        if (i, j) not in self.C:
            self.C[(i, j)] = {d: 0.0 for d in JUSTICE_DIMENSIONS}
        return self.C[(i, j)]

    def total(self, i: str, j: str) -> float:
        return float(sum(self.get(i, j).values()))

    def set(self, i: str, j: str, values: dict[str, float]) -> None:
        self.C[(i, j)] = {
            d: max(0.0, float(values.get(d, 0.0)))
            for d in JUSTICE_DIMENSIONS
        }

    def add_vector(self, i: str, j: str, cv: CompensationVector) -> None:
        """Add a CompensationVector, distributing to justice dimensions."""
        dist = cv.to_justice_dimensions()
        cur = self.get(i, j)
        self.C[(i, j)] = {d: cur[d] + dist[d] for d in JUSTICE_DIMENSIONS}

    def pairs(self) -> Iterable[tuple[str, str]]:
        return list(self.C.keys())

    def copy(self) -> CompensationMechanism:
        new = CompensationMechanism()
        new.C = {k: dict(v) for k, v in self.C.items()}
        return new