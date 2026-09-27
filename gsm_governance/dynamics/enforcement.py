"""
Policy intervention enforcement (GSM-J v0.3.0, NEW MODULE).

Reframes the constraint projection operator as a policy intervention with:
    * a designated authority,
    * an implementation cost,
    * a finite effective horizon,
    * multi-channel capability effects, and
    * passive recovery once interventions conclude.
"""

from __future__ import annotations

import numpy as np

from gsm_governance.core.parameters import (
    EPS,
    INTERVENTION_CHANNELS,
    JUSTICE_DIMENSIONS,
    C4Mode,
    EnforcementMode,
    GSMConfig,
)
from gsm_governance.core.state import ExploitationMatrix
from gsm_governance.core.system import Jurisdiction, MultiLevelGovernance


class PolicyInterventionEnforcer:
    """
    Schedule, apply, and recover from policy interventions that correct
    violations of the justice constraints.

    Attributes:
        active          — list of currently active interventions
        stats           — cumulative statistics (scheduled, completed, cost)
    """

    def __init__(
        self,
        config: GSMConfig,
        mode: EnforcementMode | None = None,
    ) -> None:
        self.config = config
        self.mode = mode or config.enforcement_mode
        self._active: list[dict] = []
        self._stats = {
            "scheduled": 0,
            "completed": 0,
            "total_cost": 0.0,
        }

    # -- properties --------------------------------------------------------

    @property
    def active(self) -> list[dict]:
        return list(self._active)

    @property
    def active_count(self) -> int:
        return len(self._active)

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    # -- scheduling --------------------------------------------------------

    def _schedule(
        self,
        authority: str,
        jurisdiction: str,
        dimension: str,
        target: float,
        current: float,
        reason: str,
    ) -> None:
        delta = target - current
        cost = self.config.intervention_cost * abs(delta)
        horizon = max(self.config.intervention_horizon, 1)
        self._active.append({
            "authority": authority,
            "jurisdiction": jurisdiction,
            "dimension": dimension,
            "from": current,
            "to": target,
            "delta_per_step": delta / horizon,
            "steps_remaining": horizon,
            "cost": cost,
            "reason": reason,
        })
        self._stats["scheduled"] += 1

    def check_and_schedule(
        self,
        governance: MultiLevelGovernance,
        exploitation: ExploitationMatrix,
    ) -> None:
        cfg = self.config
        juris = governance.jurisdictions

        # C2 — justice floor
        for uid, j in juris.items():
            authority = j.parent or uid
            for d in JUSTICE_DIMENSIONS:
                floor = cfg.justice_floors[d]
                if j.state.justice.d[d] + EPS < floor:
                    self._schedule(authority, uid, d, floor,
                                   j.state.justice.d[d], "C2_floor")

        # C3 — vulnerability-sensitive non-exploitation
        for (i, jj) in exploitation.pairs():
            if jj not in juris:
                continue
            e_tot = exploitation.total(i, jj)
            if e_tot <= EPS:
                continue
            agg_j = juris[jj].state.justice.aggregate(cfg.justice_weights)
            if agg_j + EPS < cfg.aggregate_floor:
                self._schedule(i, jj, "_exploitation_",
                               target=0.0, current=e_tot,
                               reason="C3_vulnerability")

        # C4 — vertical alignment
        mode = cfg.c4_mode
        for uid, j in juris.items():
            if not j.parent or j.parent not in juris:
                continue
            p = juris[j.parent]
            if mode in (C4Mode.PER_DIMENSION, C4Mode.HYBRID):
                for d in JUSTICE_DIMENSIONS:
                    target = cfg.phi * p.state.justice.d[d]
                    if j.state.justice.d[d] + EPS < target:
                        self._schedule(j.parent, uid, d, target,
                                       j.state.justice.d[d],
                                       "C4_per_dimension")
            if mode in (C4Mode.AGGREGATE, C4Mode.HYBRID):
                agg_j = j.state.justice.aggregate(cfg.justice_weights)
                agg_p = p.state.justice.aggregate(cfg.justice_weights)
                target_agg = cfg.phi * agg_p
                if agg_j + EPS < target_agg and agg_j > EPS:
                    scale = target_agg / agg_j
                    for d in JUSTICE_DIMENSIONS:
                        new_val = float(np.clip(
                            j.state.justice.d[d] * scale, 0.0, 1.0))
                        self._schedule(j.parent, uid, d, new_val,
                                       j.state.justice.d[d],
                                       "C4_aggregate")

    # -- application -------------------------------------------------------

    def _charge_capability_cost(
        self,
        authority_juris: Jurisdiction,
        cost_per_step: float,
    ) -> None:
        for k in INTERVENTION_CHANNELS:
            w = self.config.intervention_weights.get(k, 0.0)
            cur = getattr(authority_juris.state, k)
            new = float(np.clip(cur - w * cost_per_step, 0.0, 1.0))
            setattr(authority_juris.state, k, new)

    def apply_step(
        self,
        governance: MultiLevelGovernance,
        exploitation: ExploitationMatrix,
    ) -> None:
        juris = governance.jurisdictions
        horizon = max(self.config.intervention_horizon, 1)
        remaining: list[dict] = []

        for iv in self._active:
            uid = iv["jurisdiction"]
            if uid not in juris:
                continue
            j = juris[uid]

            if iv["dimension"] == "_exploitation_":
                for (ii, jj) in exploitation.pairs():
                    if jj == uid:
                        exploitation.reduce(ii, jj, iv["cost"] / horizon)
            else:
                d = iv["dimension"]
                j.state.justice.d[d] = float(np.clip(
                    j.state.justice.d[d] + iv["delta_per_step"], 0.0, 1.0))

            if iv["authority"] in juris:
                auth = juris[iv["authority"]]
                per_step = iv["cost"] / horizon
                self._charge_capability_cost(auth, per_step)
                self._stats["total_cost"] += per_step

            iv["steps_remaining"] -= 1
            if iv["steps_remaining"] > 0:
                remaining.append(iv)
            else:
                self._stats["completed"] += 1

        self._active = remaining

    def apply_recovery(self, governance: MultiLevelGovernance) -> None:
        if self._active:
            return
        for j in governance.jurisdictions.values():
            for k in INTERVENTION_CHANNELS:
                rho = self.config.recovery.get(k, 0.0)
                baseline = j.baseline(k)
                cur = getattr(j.state, k)
                new = float(np.clip(cur + rho * (baseline - cur), 0.0, 1.0))
                setattr(j.state, k, new)

    # -- orchestration -----------------------------------------------------

    def enforce(
        self,
        governance: MultiLevelGovernance,
        exploitation: ExploitationMatrix,
    ) -> None:
        self.check_and_schedule(governance, exploitation)
        self.apply_step(governance, exploitation)
        self.apply_recovery(governance)

    def reset(self) -> None:
        self._active.clear()
        self._stats = {"scheduled": 0, "completed": 0, "total_cost": 0.0}