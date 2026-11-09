"""Compensation vector (Section 3.5, Table 7)."""
from dataclasses import dataclass
from .config import GSMConfig, DIMENSIONS

_TARGETS = {
    "fiscal":           {"distributive"},
    "infrastructural":  {"distributive", "corrective"},
    "representational": {"procedural", "recognition"},
    "regulatory":       {"procedural", "recognition", "intergenerational"},
    "future":           {"intergenerational"},
    "restitutional":    {"corrective"},
}


@dataclass
class CompensationVector:
    fiscal: float = 0.0
    infrastructural: float = 0.0
    representational: float = 0.0
    regulatory: float = 0.0
    future: float = 0.0
    restitutional: float = 0.0

    def total(self) -> float:
        return (self.fiscal + self.infrastructural + self.representational
                + self.regulatory + self.future + self.restitutional)

    def is_adequate(self, exploitation: float, config: GSMConfig) -> bool:
        """Adequate iff lambda_j * Comp >= E (Section 3.5). Conservative: lambda=1."""
        return self.total() + config.epsilon >= exploitation

    def channel_coverage(self, dimension: str) -> bool:
        return any(dimension in targets for targets in _TARGETS.values())
