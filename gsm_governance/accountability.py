"""Dimension-specific cross-level accountability (Section 3.7)."""
from typing import Dict, List
from .config import GSMConfig, DIMENSIONS


class Accountability:
    def __init__(self, config: GSMConfig):
        self.config = config
        self.A: Dict[str, Dict[str, float]] = {}

    def initialize(self, jurisdictions: List):
        for j in jurisdictions:
            self.A[j.id] = dict(j.state.capabilities)

    def update(self, jurisdictions: List):
        """A^{d,l}(t+1) = A^{d,l}(t) + lambda^{pd} (J^{d,l+1} - J^{d,l}) (Section 3.7)."""
        for j in jurisdictions:
            if j.parent is None:
                continue
            if j.id not in self.A:
                self.A[j.id] = dict(j.state.capabilities)
            for d in DIMENSIONS:
                gap = j.state.justice[d] - j.parent.state.justice[d]
                self.A[j.id][d] += self.config.lambda_pd[d] * gap
                self.A[j.id][d] = max(0.0, min(1.0, self.A[j.id][d]))
