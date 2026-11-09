"""Policy intervention with cost, horizon, channel effects, and recovery (Section 4.1)."""
from dataclasses import dataclass
from typing import Dict, List, Optional
from .config import GSMConfig, DIMENSIONS, CAPABILITIES


@dataclass
class Intervention:
    jurisdiction_id: str
    start_t: int
    channel: str
    magnitude: float
    dimension_target: Optional[str] = None
    authority: Optional[str] = None


_CHANNEL_JUSTICE = {
    "fiscal":           {"distributive": +0.5},
    "infrastructural":  {"distributive": +0.3, "corrective": +0.2},
    "representational": {"procedural": +0.3, "recognition": +0.3},
    "regulatory":       {"procedural": +0.1, "recognition": +0.2, "intergenerational": +0.2},
    "future":           {"intergenerational": +0.5},
    "restitutional":    {"corrective": +0.5},
}
_CHANNEL_CAPABILITY = {
    "fiscal":           {"competence": +0.1},
    "infrastructural":  {"competence": +0.1, "cohesion": +0.05},
    "representational": {"accountability": +0.1, "cohesion": +0.05},
    "regulatory":       {"accountability": +0.1, "learning": +0.05},
    "future":           {"continuity": +0.1},
    "restitutional":    {"cohesion": +0.1},
}


class PolicyInterventionEnforcer:
    def __init__(self, config: GSMConfig):
        self.config = config
        self.active: List[Intervention] = []
        self._recovery: Dict[str, Dict[str, float]] = {}

    def add(self, intervention: Intervention):
        self.active.append(intervention)

    def apply(self, t: int, jurisdictions: List):
        by_id = {j.id: j for j in jurisdictions}
        still_active = []
        deltas_by_j = {j.id: {d: 0.0 for d in DIMENSIONS} for j in jurisdictions}
        cap_deltas = {j.id: {c: 0.0 for c in CAPABILITIES} for j in jurisdictions}
        cost_by_j = {j.id: 0.0 for j in jurisdictions}

        for iv in self.active:
            j = by_id.get(iv.jurisdiction_id)
            if j is None:
                continue
            age = t - iv.start_t
            if age < 0 or age > self.config.tau_int:
                if age > self.config.tau_int:
                    d = self._recovery.setdefault(
                        iv.jurisdiction_id, {k: 0.0 for k in DIMENSIONS})
                    for dim, eff in _CHANNEL_JUSTICE.get(iv.channel, {}).items():
                        d[dim] -= self.config.recovery_rate * eff * iv.magnitude
                continue
            still_active.append(iv)

            for dim, eff in _CHANNEL_JUSTICE.get(iv.channel, {}).items():
                deltas_by_j[j.id][dim] += (
                    eff * iv.magnitude * self.config.omega_k.get(iv.channel, 0.2))
            for cap, eff in _CHANNEL_CAPABILITY.get(iv.channel, {}).items():
                cap_deltas[j.id][cap] += (
                    eff * iv.magnitude * self.config.omega_k.get(iv.channel, 0.2))
            cost_by_j[j.id] += self.config.kappa_int * iv.magnitude

        for j in jurisdictions:
            for dim in DIMENSIONS:
                j.state.justice[dim] += deltas_by_j[j.id][dim]
            for cap in CAPABILITIES:
                j.state.capabilities[cap] += cap_deltas[j.id][cap]
            j.state.capabilities["cohesion"] -= 0.5 * cost_by_j[j.id]
            j.state.capabilities["continuity"] -= 0.5 * cost_by_j[j.id]

        for jid, rec in self._recovery.items():
            j = by_id.get(jid)
            if j is None:
                continue
            for dim, dv in rec.items():
                j.state.justice[dim] += dv
                rec[dim] *= 0.5

        self.active = still_active
        for j in jurisdictions:
            j.state.clip()

    def predicted_frequency_ceiling(self) -> float:
        """Endogenous ceiling on aggressive interventions (H7)."""
        return 1.0 / max(self.config.kappa_int, 1e-6)
