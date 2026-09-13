"""GSM multi-level governance research library."""
from .core.parameters import GSMConfig, LevelParameters, WelfareWeights
from .core.state import FlourishingState, GovernanceState, Observation
from .core.system import Jurisdiction, MultiLevelGovernance
from .dynamics.constraint import BoundedNonExploitationConstraint, CompensationVector, ConstraintResult, ThresholdFunction
from .dynamics.simulation import Simulation, SimulationHistory
from .dynamics.transitions import TransitionModel
from .metrics.indices import compute_gsi, compute_hfi
from .metrics.misalignment import context_sensitive_misalignment, vertical_misalignment
from .metrics.resilience import resilience_metrics
from .metrics.welfare import compute_welfare, distribution_sensitive_hfi
__version__ = "0.1.0"
__all__ = ["GSMConfig","LevelParameters","WelfareWeights","GovernanceState","FlourishingState","Observation","Jurisdiction","MultiLevelGovernance","BoundedNonExploitationConstraint","CompensationVector","ConstraintResult","ThresholdFunction","Simulation","SimulationHistory","TransitionModel","compute_gsi","compute_hfi","compute_welfare","distribution_sensitive_hfi","context_sensitive_misalignment","vertical_misalignment","resilience_metrics"]
