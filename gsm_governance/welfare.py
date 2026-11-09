"""Dimension-specific welfare (Section 4.3).

Modes:
    quadratic (default):  W = sum_l sum_i sum_d w_d [ gamma_d J - delta_d (1-J)^2 ]
    linear_floor:         W = sum_l sum_i [ sum_d w_d gamma_d J
                                              - sum_d w_d delta_d max(0, floor_d - J) ]
"""
from typing import Dict, List
from .config import GSMConfig, DIMENSIONS


class WelfareEvaluator:
    def __init__(self, config: GSMConfig):
        self.config = config

    def welfare(self, jurisdictions: List, mode: str = None) -> Dict[str, float]:
        mode = mode or self.config.welfare_mode
        W_base = 0.0

        for j in jurisdictions:
            if mode == "quadratic":
                for d in DIMENSIONS:
                    J = j.state.justice[d]
                    w = self.config.weights[d]
                    W_base += w * (
                        self.config.gamma_w[d] * J
                        - self.config.delta_w[d] * (1.0 - J) ** 2
                    )
            elif mode == "linear_floor":
                for d in DIMENSIONS:
                    J = j.state.justice[d]
                    w = self.config.weights[d]
                    W_base += w * self.config.gamma_w[d] * J
                    shortfall = max(0.0, self.config.floors[d] - J)
                    W_base -= w * self.config.delta_w[d] * shortfall
            else:
                raise ValueError(f"unknown welfare mode {mode}")

        return {
            "total": W_base,
            "base": W_base,
            "exploitation_penalty": 0.0,
            "compensation_credit": 0.0,
        }

    def welfare_enhanced(
        self,
        jurisdictions: List,
        exploitation: Dict[tuple, float],
        compensation: Dict[tuple, object],
    ) -> Dict[str, float]:
        """W* = W + exploitation penalties + compensation credits (Section 4.3)."""
        base = self.welfare(jurisdictions)
        W_expl = -sum(exploitation.values())
        W_comp = sum(c.total() for c in compensation.values())
        return {
            "total": base["base"] + W_expl + W_comp,
            "base": base["base"],
            "exploitation_penalty": W_expl,
            "compensation_credit": W_comp,
        }

    def is_prioritarian(self) -> bool:
        return all(
            self.config.delta_w[d] > self.config.gamma_w[d]
            for d in DIMENSIONS
        )
