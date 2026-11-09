"""gsm-governance: reference implementation of the computational theory of
justice-centered multi-level governance (GSM-J). Version 0.4.0.

The theory is described in:
    Wang, H. A Computational Theory of Justice-Centered Multi-Level Governance
    for Human Flourishing under Bounded Non-Exploitation.

Public API:
    GSMConfig, State, Jurisdiction
    JusticeInteractionMatrix
    check_c1, check_c2, check_c3, check_c4
    WelfareEvaluator
    Accountability
    CompensationVector
    PolicyInterventionEnforcer
    Simulation
    load_stylized_nordic
"""

from .config import (
    GSMConfig, DIMENSIONS, CAPABILITIES,
    CONTESTED_PAIRS, SINGLE_COMPONENT_TENSION_PAIRS, SINGLE_COMPONENT_SYNERGY_PAIRS,
)
from .entities import State, Jurisdiction
from .justice import JusticeInteractionMatrix
from .dynamics import justice_step, capability_step
from .constraints import check_c1, check_c2, check_c3, check_c4, check_all
from .welfare import WelfareEvaluator
from .accountability import Accountability
from .compensation import CompensationVector
from .enforcement import PolicyInterventionEnforcer, Intervention
from .simulation import Simulation
from .data import load_stylized_nordic, load_stylized_nordic_raw

__version__ = "0.4.0"
__all__ = [
    "GSMConfig", "DIMENSIONS", "CAPABILITIES",
    "CONTESTED_PAIRS", "SINGLE_COMPONENT_TENSION_PAIRS", "SINGLE_COMPONENT_SYNERGY_PAIRS",
    "State", "Jurisdiction",
    "JusticeInteractionMatrix",
    "justice_step", "capability_step",
    "check_c1", "check_c2", "check_c3", "check_c4", "check_all",
    "WelfareEvaluator",
    "Accountability",
    "CompensationVector",
    "PolicyInterventionEnforcer", "Intervention",
    "Simulation",
    "load_stylized_nordic", "load_stylized_nordic_raw",
]
