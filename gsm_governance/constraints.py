"""Justice-centered constraints C1-C4 (Section 3.6)."""
from typing import Dict, List, Tuple

from .compensation import CompensationVector
from .config import DIMENSIONS, GSMConfig


def check_c1(
    jurisdictions: List,
    exploitation: Dict[Tuple[str, str], float],
    compensation: Dict[Tuple[str, str], CompensationVector],
    config: GSMConfig,
) -> List[Tuple[str, str]]:
    """C1 - bounded non-exploitation (Section 3.6.1)."""
    by_id = {j.id: j for j in jurisdictions}
    violations = []
    for (i, j), e in exploitation.items():
        if e <= 0.0:
            continue
        tau_eff = by_id[j].tau if j in by_id else config.default_tau
        if e <= tau_eff + config.epsilon:
            continue
        comp = compensation.get((i, j))
        if comp is None or not comp.is_adequate(e, config):
            violations.append((i, j))
    return violations


def check_c2(jurisdictions: List, config: GSMConfig) -> List[Tuple[str, str, float]]:
    """C2 - dimension-specific justice floor (Section 3.6.2)."""
    violations = []
    for j in jurisdictions:
        for d in DIMENSIONS:
            v = j.state.justice[d]
            if v + config.epsilon < config.floors[d]:
                violations.append((j.id, d, v))
    return violations


def effective_tau(jurisdiction, config: GSMConfig) -> float:
    """Effective tolerance threshold, applying C3 (Section 3.6.3)."""
    agg = sum(jurisdiction.state.justice.values()) / len(DIMENSIONS)
    if agg + config.epsilon < config.aggregate_floor:
        return config.phi_vuln * jurisdiction.tau
    return jurisdiction.tau


def check_c3(jurisdictions: List, config: GSMConfig) -> List[str]:
    """C3 - vulnerability-sensitive non-exploitation (Section 3.6.3).

    Returns ids of jurisdictions currently subject to a reduced threshold.
    """
    return [
        j.id for j in jurisdictions
        if effective_tau(j, config) < j.tau - config.epsilon
    ]


def check_c4(jurisdictions: List, config: GSMConfig) -> List[Tuple[str, str, float]]:
    """C4 - dimension-wise vertical alignment (Section 3.6.4).

    Violation when J_child^d < J_parent^d - phi_d.
    Returns (child_id, dimension, shortfall) where shortfall > 0.
    """
    violations = []
    for child in jurisdictions:
        if child.parent is None:
            continue
        for d in DIMENSIONS:
            margin = child.parent.state.justice[d] - config.phi_d[d]
            shortfall = margin - child.state.justice[d]
            if shortfall > config.epsilon:
                violations.append((child.id, d, shortfall))
    return violations


def check_all(jurisdictions, exploitation, compensation, config):
    """Run all constraint checks and return a summary dict."""
    return {
        "c1": check_c1(jurisdictions, exploitation, compensation, config),
        "c2": check_c2(jurisdictions, config),
        "c3": check_c3(jurisdictions, config),
        "c4": check_c4(jurisdictions, config),
    }
