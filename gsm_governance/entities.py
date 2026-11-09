"""State and jurisdiction entities."""
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from .config import DIMENSIONS, CAPABILITIES


@dataclass
class State:
    """The state vector x_i^(l) = [A, C, S, T, L, J] (Section 3.2)."""
    capabilities: Dict[str, float] = field(default_factory=lambda: {c: 0.5 for c in CAPABILITIES})
    justice: Dict[str, float] = field(default_factory=lambda: {d: 0.5 for d in DIMENSIONS})

    def aggregate_justice(self, weights: Dict[str, float]) -> float:
        return sum(weights[d] * self.justice[d] for d in DIMENSIONS)

    def clip(self):
        for c in CAPABILITIES:
            self.capabilities[c] = max(0.0, min(1.0, self.capabilities[c]))
        for d in DIMENSIONS:
            self.justice[d] = max(0.0, min(1.0, self.justice[d]))

    def copy(self) -> "State":
        return State(
            capabilities=dict(self.capabilities),
            justice=dict(self.justice),
        )


@dataclass
class Jurisdiction:
    id: str
    level: int
    state: State = field(default_factory=State)
    parent: Optional["Jurisdiction"] = None
    children: List["Jurisdiction"] = field(default_factory=list)
    tau: float = 0.05

    def add_child(self, child: "Jurisdiction"):
        child.parent = self
        self.children.append(child)
