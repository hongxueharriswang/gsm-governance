"""
GSM-J v0.3.0 — Justice as a Governance Capability.

A computational systems model of multi-level governance for human
flourishing under bounded non-exploitation.

Reference:
    Wang, H. H. (2026). Justice as a Governance Capability: A Computational
    Systems Model of Multi-Level Governance for Human Flourishing under
    Bounded Non-Exploitation. Preprints.org.
    https://doi.org/10.20944/preprints202609.0964.v2
"""

__version__ = "0.3.0"

# --- constants ------------------------------------------------------------
from gsm_governance.core.parameters import (
    BASE_CAPABILITIES,
    INTERVENTION_CHANNELS,
    JUSTICE_DIMENSIONS,
    C4Mode,
    EnforcementMode,
    GSMConfig,
    JusticeInteractionMatrix,
    MJRegime,
)

# --- state and system -----------------------------------------------------
from gsm_governance.core.state import (
    CompensationMechanism,
    CompensationVector,
    ExploitationMatrix,
    FlourishingState,
    GovernanceState,
    JusticeState,
)
from gsm_governance.core.system import (
    Jurisdiction,
    MultiLevelGovernance,
)

# --- dynamics -------------------------------------------------------------
from gsm_governance.dynamics.constraint import (
    BoundedNonExploitationConstraint,
    ConstraintChecker,
    JusticeConstraintSet,
)
from gsm_governance.dynamics.enforcement import PolicyInterventionEnforcer
from gsm_governance.dynamics.simulation import Simulation
from gsm_governance.dynamics.transitions import (
    base_capability_step,
    justice_step,
    update_accountability_dimension_specific,
)

# --- metrics --------------------------------------------------------------
from gsm_governance.metrics.indices import (
    exploitation_index,
    gsi,
    hfi,
    justice_floor_violations,
    justice_index,
)
from gsm_governance.metrics.misalignment import (
    justice_misalignment,
    misalignment,
)
from gsm_governance.metrics.resilience import resilience
from gsm_governance.metrics.welfare import (
    welfare,
    welfare_components,
    welfare_dimension_specific,
)

# --- utils ----------------------------------------------------------------
from gsm_governance.utils.normalization import (
    min_max_normalize,
    z_score_normalize,
)

__all__ = [
    "__version__",
    # constants
    "JUSTICE_DIMENSIONS",
    "BASE_CAPABILITIES",
    "INTERVENTION_CHANNELS",
    "C4Mode",
    "MJRegime",
    "EnforcementMode",
    "GSMConfig",
    "JusticeInteractionMatrix",
    # state
    "JusticeState",
    "GovernanceState",
    "FlourishingState",
    "CompensationVector",
    "ExploitationMatrix",
    "CompensationMechanism",
    # system
    "Jurisdiction",
    "MultiLevelGovernance",
    # dynamics
    "BoundedNonExploitationConstraint",
    "JusticeConstraintSet",
    "ConstraintChecker",
    "PolicyInterventionEnforcer",
    "Simulation",
    "justice_step",
    "base_capability_step",
    "update_accountability_dimension_specific",
    # metrics
    "gsi",
    "hfi",
    "justice_index",
    "justice_floor_violations",
    "exploitation_index",
    "misalignment",
    "justice_misalignment",
    "resilience",
    "welfare",
    "welfare_dimension_specific",
    "welfare_components",
    # utils
    "min_max_normalize",
    "z_score_normalize",
]