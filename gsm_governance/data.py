"""Data loaders for the illustrative stylized-Nordic demonstration (Section 6).

These are illustrative profiles, not measurements of any real country. The
name "stylized_nordic" is deliberate: the paper's Section 6 states that no
actual country is claimed to instantiate the model.
"""
from typing import Dict, List
from .entities import State, Jurisdiction
from .config import DIMENSIONS, CAPABILITIES

_STYLIZED_PROFILES: Dict[int, Dict[str, float]] = {
    1: {"accountability": 0.85, "competence": 0.80, "cohesion": 0.82,
        "continuity": 0.78, "learning": 0.80,
        "distributive": 0.78, "procedural": 0.80, "recognition": 0.62,
        "corrective": 0.45, "intergenerational": 0.55},
    2: {"accountability": 0.72, "competence": 0.70, "cohesion": 0.75,
        "continuity": 0.68, "learning": 0.72,
        "distributive": 0.70, "procedural": 0.72, "recognition": 0.58,
        "corrective": 0.40, "intergenerational": 0.50},
    3: {"accountability": 0.68, "competence": 0.65, "cohesion": 0.70,
        "continuity": 0.65, "learning": 0.68,
        "distributive": 0.65, "procedural": 0.68, "recognition": 0.55,
        "corrective": 0.35, "intergenerational": 0.45},
}


def _make_state(profile: Dict[str, float]) -> State:
    return State(
        capabilities={c: profile[c] for c in CAPABILITIES},
        justice={d: profile[d] for d in DIMENSIONS},
    )


def load_stylized_nordic() -> List[Jurisdiction]:
    """Return three illustrative jurisdictions in a parent-child chain."""
    j1 = Jurisdiction(id="national", level=1,
                      state=_make_state(_STYLIZED_PROFILES[1]), tau=0.05)
    j2 = Jurisdiction(id="province", level=2,
                      state=_make_state(_STYLIZED_PROFILES[2]), tau=0.05)
    j3 = Jurisdiction(id="municipality", level=3,
                      state=_make_state(_STYLIZED_PROFILES[3]), tau=0.05)
    j1.add_child(j2)
    j2.add_child(j3)
    return [j1, j2, j3]


def load_stylized_nordic_raw() -> Dict[int, Dict[str, float]]:
    return {k: dict(v) for k, v in _STYLIZED_PROFILES.items()}


def load_denmark_raw() -> Dict[int, Dict[str, float]]:
    """Deprecated. Use load_stylized_nordic_raw."""
    import warnings
    warnings.warn(
        "load_denmark_raw is deprecated; use load_stylized_nordic_raw. "
        "The paper's Section 6 replaces the Denmark case with a stylized "
        "Nordic democracy and states that no actual country is claimed to "
        "instantiate the model.",
        DeprecationWarning, stacklevel=2,
    )
    return load_stylized_nordic_raw()
