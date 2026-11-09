"""End-to-end simulation engine."""
import random
from typing import Dict, List, Optional, Tuple
from .config import GSMConfig, DIMENSIONS
from .entities import Jurisdiction
from .justice import JusticeInteractionMatrix
from .dynamics import justice_step, capability_step
from .constraints import check_all
from .welfare import WelfareEvaluator
from .accountability import Accountability
from .enforcement import PolicyInterventionEnforcer


class Simulation:
    def __init__(self, config: GSMConfig, jurisdictions: List[Jurisdiction],
                 interaction: Optional[JusticeInteractionMatrix] = None):
        self.config = config
        self.jurisdictions = jurisdictions
        if config.seed is not None:
            random.seed(config.seed)
        self.interaction = interaction or JusticeInteractionMatrix(
            m_max=config.m_max, symmetry=config.symmetry,
        )
        self.welfare = WelfareEvaluator(config)
        self.accountability = Accountability(config)
        self.accountability.initialize(jurisdictions)
        self.enforcer = PolicyInterventionEnforcer(config)
        self.t = 0
        self.history: List[Dict] = []

    def _exploitation(
        self,
        prev_justice: Dict[str, Dict[str, float]],
        prev_cap: Dict[str, Dict[str, float]],
    ) -> Dict[Tuple[str, str], float]:
        """Illustrative exploitation estimate. Production use should supply
        calibration per Section 6.3."""
        out: Dict[Tuple[str, str], float] = {}
        for j in self.jurisdictions:
            if j.parent is None:
                continue
            p = j.parent
            e = 0.0
            for d in DIMENSIONS:
                gain = p.state.justice[d] - prev_justice[p.id][d]
                loss = prev_justice[j.id][d] - j.state.justice[d]
                if gain > 0 and loss > 0:
                    e += 0.5 * min(gain, loss)
            if e > 0:
                out[(p.id, j.id)] = e
        return out

    def step(self) -> Dict:
        prev_J = {j.id: dict(j.state.justice) for j in self.jurisdictions}
        prev_C = {j.id: dict(j.state.capabilities) for j in self.jurisdictions}

        self.enforcer.apply(self.t, self.jurisdictions)
        exploitation = self._exploitation(prev_J, prev_C)

        for j in self.jurisdictions:
            dJ = justice_step(
                j, self.config, self.interaction,
                exploitation_by_dim={
                    d: sum(v for (a, b), v in exploitation.items()
                           if a == (j.parent.id if j.parent else "") and b == j.id)
                    / len(DIMENSIONS)
                    for d in DIMENSIONS
                },
            )
            for d in DIMENSIONS:
                j.state.justice[d] += dJ[d]
            j.state.clip()

        for j in self.jurisdictions:
            dC = capability_step(j, self.config)
            for c, dv in dC.items():
                j.state.capabilities[c] += dv
            j.state.clip()

        self.accountability.update(self.jurisdictions)

        compensation: Dict = {}
        constraints = check_all(self.jurisdictions, exploitation, compensation, self.config)
        W = self.welfare.welfare_enhanced(self.jurisdictions, exploitation, compensation)

        row = {
            "t": self.t,
            "welfare": W,
            "violations": constraints,
            "n_exploitations": len(exploitation),
            "total_exploitation": sum(exploitation.values()),
        }
        self.history.append(row)
        self.t += 1
        return row

    def run(self, n_steps: int) -> List[Dict]:
        return [self.step() for _ in range(n_steps)]
