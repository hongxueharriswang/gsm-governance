"""
Multi-level governance hierarchy.

Jurisdiction       — a governance unit at a given level.
MultiLevelGovernance — container managing the hierarchy.
"""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np

from gsm_governance.core.parameters import (
    BASE_CAPABILITIES,
    INTERVENTION_CHANNELS,
)
from gsm_governance.core.state import GovernanceState, JusticeState

# ===========================================================================
# Jurisdiction
# ===========================================================================

class Jurisdiction:
    """A governance unit at a given level in the hierarchy."""

    def __init__(
        self,
        uid: str,
        level: int,
        state: GovernanceState | None = None,
    ) -> None:
        self.uid = uid
        self.level = level
        self.state = state or GovernanceState()
        self.parent: str | None = None
        self.children: list[str] = []
        self.neighbours: list[str] = []
        self._baseline: dict[str, float] = {
            k: getattr(self.state, k) for k in INTERVENTION_CHANNELS
        }

    # -- capability accessors (backward-compatible) ------------------------

    @property
    def capabilities(self) -> dict[str, float]:
        return self.state.capabilities()

    @property
    def justice(self) -> JusticeState:
        return self.state.justice

    def set_baseline(self) -> None:
        """Refresh baseline capability values (used by recovery)."""
        self._baseline = {k: getattr(self.state, k)
                          for k in INTERVENTION_CHANNELS}

    def baseline(self, key: str) -> float:
        return self._baseline.get(key, getattr(self.state, key))

    def __repr__(self) -> str:
        return (
            f"Jurisdiction(uid={self.uid!r}, level={self.level}, "
            f"J={self.state.justice})"
        )


# ===========================================================================
# MultiLevelGovernance
# ===========================================================================

class MultiLevelGovernance:
    """
    Container for a multi-level governance hierarchy.

    Backward-compatible with v0.2.0: supports construction from a single
    jurisdiction, iteration, lookup by uid, and hierarchy traversal.
    """

    def __init__(self, config=None) -> None:
        from gsm_governance.core.parameters import GSMConfig
        self.config = config or GSMConfig()
        self.jurisdictions: dict[str, Jurisdiction] = {}

    # -- construction ------------------------------------------------------

    @classmethod
    def from_single_jurisdiction(
        cls,
        uid: str = "root",
        level: int = 4,
        config=None,
    ) -> MultiLevelGovernance:
        g = cls(config=config)
        g.add_jurisdiction(uid, level=level)
        return g

    def add_jurisdiction(
        self,
        uid: str,
        level: int,
        capabilities: dict[str, float] | None = None,
        justice: JusticeState | None = None,
    ) -> Jurisdiction:
        if uid in self.jurisdictions:
            raise ValueError(f"jurisdiction {uid!r} already exists")
        state = GovernanceState()
        if capabilities:
            for k, v in capabilities.items():
                if k in BASE_CAPABILITIES:
                    state.set_capability(k, v)
        if justice:
            state.justice = justice
        j = Jurisdiction(uid, level, state=state)
        self.jurisdictions[uid] = j
        return j

    def remove_jurisdiction(self, uid: str) -> None:
        if uid not in self.jurisdictions:
            return
        j = self.jurisdictions.pop(uid)
        if j.parent and j.parent in self.jurisdictions:
            parent = self.jurisdictions[j.parent]
            if uid in parent.children:
                parent.children.remove(uid)
        for child in list(j.children):
            if child in self.jurisdictions:
                self.jurisdictions[child].parent = None
        for nb in list(j.neighbours):
            if nb in self.jurisdictions:
                nbr = self.jurisdictions[nb]
                if uid in nbr.neighbours:
                    nbr.neighbours.remove(uid)

    # -- linking -----------------------------------------------------------

    def link_vertical(self, parent: str, child: str) -> None:
        if parent not in self.jurisdictions:
            raise KeyError(f"unknown parent: {parent}")
        if child not in self.jurisdictions:
            raise KeyError(f"unknown child: {child}")
        p = self.jurisdictions[parent]
        c = self.jurisdictions[child]
        if child not in p.children:
            p.children.append(child)
        c.parent = parent

    def link_horizontal(self, a: str, b: str) -> None:
        if a not in self.jurisdictions or b not in self.jurisdictions:
            raise KeyError(f"unknown jurisdiction in {a}, {b}")
        ja = self.jurisdictions[a]
        jb = self.jurisdictions[b]
        if b not in ja.neighbours:
            ja.neighbours.append(b)
        if a not in jb.neighbours:
            jb.neighbours.append(a)

    # -- access ------------------------------------------------------------

    def __getitem__(self, uid: str) -> Jurisdiction:
        return self.jurisdictions[uid]

    def __contains__(self, uid: str) -> bool:
        return uid in self.jurisdictions

    def __iter__(self) -> Iterator[Jurisdiction]:
        return iter(self.jurisdictions.values())

    def __len__(self) -> int:
        return len(self.jurisdictions)

    def by_level(self, level: int) -> list[Jurisdiction]:
        return [j for j in self.jurisdictions.values() if j.level == level]

    def levels(self) -> list[int]:
        return sorted({j.level for j in self.jurisdictions.values()})

    def roots(self) -> list[Jurisdiction]:
        return [j for j in self.jurisdictions.values() if j.parent is None]

    def aggregate_justice(self) -> float:
        if not self.jurisdictions:
            return 0.0
        return float(np.mean([
            j.state.justice.aggregate(self.config.justice_weights)
            for j in self.jurisdictions.values()
        ]))

    def __repr__(self) -> str:
        return (
            f"MultiLevelGovernance(n={len(self.jurisdictions)}, "
            f"levels={self.levels()})"
        )