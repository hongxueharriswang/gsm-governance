"""
Simulation loop for GSM-J.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from gsm_governance.core.parameters import (
    GSMConfig,
    JusticeInteractionMatrix,
    MJRegime,
)
from gsm_governance.core.state import (
    CompensationMechanism,
    ExploitationMatrix,
)
from gsm_governance.core.system import MultiLevelGovernance
from gsm_governance.dynamics.constraint import (
    BoundedNonExploitationConstraint,
    ConstraintChecker,
)
from gsm_governance.dynamics.enforcement import PolicyInterventionEnforcer
from gsm_governance.dynamics.transitions import (
    base_capability_step,
    justice_step,
    update_accountability_dimension_specific,
)
from gsm_governance.metrics.welfare import welfare_dimension_specific


class Simulation:
    """
    Top-level simulation runner for GSM-J.

    Usage:
        sim = Simulation(governance, config, M_J)
        history = sim.run(steps=500)
    """

    def __init__(
        self,
        governance: MultiLevelGovernance,
        config: GSMConfig | None = None,
        M_J: JusticeInteractionMatrix | None = None,
        constraint: BoundedNonExploitationConstraint | None = None,
        enforcer: PolicyInterventionEnforcer | None = None,
        seed: int | None = None,
    ) -> None:
        self.governance = governance
        self.config = config or governance.config
        self.M_J = M_J or JusticeInteractionMatrix(regime=MJRegime.SYMMETRIC)
        self.exploitation = ExploitationMatrix()
        self.compensation = CompensationMechanism()
        self.checker = ConstraintChecker(self.config)
        self.enforcer = enforcer or PolicyInterventionEnforcer(self.config)
        self.constraint = constraint or BoundedNonExploitationConstraint(
            tau=self.config.tau)

        self.t = 0.0
        self.history: list[dict] = []
        self._rng = np.random.default_rng(seed)

    # -- injection of exploitation / compensation --------------------------

    def set_exploitation(self, i: str, j: str, values: dict[str, float]) -> None:
        self.exploitation.set(i, j, values)

    def set_compensation(self, i: str, j: str, values: dict[str, float]) -> None:
        self.compensation.set(i, j, values)

    # -- welfare -----------------------------------------------------------

    def base_welfare(self) -> float:
        juris = self.governance.jurisdictions
        if not juris:
            return 0.0
        total = 0.0
        for j in juris.values():
            total += j.state.A + j.state.C + j.state.S + j.state.T + j.state.L
        return total / (5 * len(juris))

    def welfare(self) -> float:
        return welfare_dimension_specific(
            self.base_welfare(), self.governance, self.config)

    # -- stepping ----------------------------------------------------------

    def step(self) -> None:
        dt = self.config.dt
        juris = self.governance.jurisdictions

        # 1. Base capability drift
        for j in juris.values():
            base_capability_step(j, self.governance, self.config, dt)

        # 2. Justice dynamics
        for j in juris.values():
            justice_step(
                j, self.governance, self.exploitation,
                self.compensation, self.config, self.M_J, dt,
            )

        # 3. Cross-level accountability (dimension-specific)
        for j in juris.values():
            update_accountability_dimension_specific(
                j, self.governance, self.config)

        # 4. Justice suppression of exploitation
        for (i, jj) in self.exploitation.pairs():
            if i not in juris or jj not in juris:
                continue
            ji = juris[i].state.justice.aggregate(self.config.justice_weights)
            jj_agg = juris[jj].state.justice.aggregate(self.config.justice_weights)
            m = min(ji, jj_agg)
            factor = float(np.exp(-dt * self.config.mu * m))
            self.exploitation.E[(i, jj)] = {
                d: v * factor for d, v in self.exploitation.E[(i, jj)].items()
            }

        # 5. Constraint enforcement via policy intervention
        self.enforcer.enforce(self.governance, self.exploitation)

        self.t += dt

    # -- recording ---------------------------------------------------------

    def record(self) -> None:
        juris = self.governance.jurisdictions
        if not juris:
            return
        from gsm_governance.core.parameters import JUSTICE_DIMENSIONS
        dim_means = {
            d: float(np.mean([j.state.justice.d[d] for j in juris.values()]))
            for d in JUSTICE_DIMENSIONS
        }
        mean_justice = float(np.mean([
            j.state.justice.aggregate(self.config.justice_weights)
            for j in juris.values()
        ]))
        self.history.append({
            "t": self.t,
            "W_star": self.welfare(),
            "mean_justice": mean_justice,
            "dim_means": dim_means,
            "C1_violations": len(self.checker.C1(
                self.exploitation, self.compensation)),
            "C2_violations": len(self.checker.C2(juris)),
            "C3_violations": len(self.checker.C3(
                self.exploitation, juris)),
            "C4_violations": len(self.checker.C4(juris)),
            "active_interventions": self.enforcer.active_count,
            "total_cost": self.enforcer.stats["total_cost"],
        })

    def run(
        self,
        steps: int,
        callback: Callable[[Simulation], None] | None = None,
    ) -> list[dict]:
        for _ in range(steps):
            self.step()
            self.record()
            if callback:
                callback(self)
        return self.history

    def reset(self) -> None:
        self.t = 0.0
        self.history.clear()
        self.enforcer.reset()