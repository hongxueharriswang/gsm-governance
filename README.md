# gsm-governance

**Justice as a Governance Capability: A Computational Systems Model of Multi-Level Governance for Human Flourishing under Bounded Non-Exploitation**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Preprint](https://img.shields.io/badge/preprint-preprints.org-orange)](https://doi.org/10.20944/preprints202609.0964.v2)
[![Version](https://img.shields.io/badge/version-0.3.0-green.svg)](https://github.com/hongxueharriswang/gsm-governance)

`gsm-governance` is the reference implementation of **GSM-J**, a computational systems model of multi-level governance in which justice is treated not as an external normative constraint but as a **productive, fragile, multi-level governance capability** that co-evolves with accountability, competence, cohesion, continuity, and learning.

The library supports the full model specification: state-space dynamics, four justice constraints (C1–C4), dimension-specific cross-level accountability, a signed justice interaction matrix \( M_J \), dimension-specific prioritarian welfare, and constraint enforcement via multi-channel policy intervention with cost, delay, and recovery.

---

## Table of contents

- [What's new in 0.3.0](#whats-new-in-030)
- [Installation](#installation)
- [Quick start](#quick-start)
- [The model](#the-model)
  - [State vector](#state-vector)
  - [Justice capability](#justice-capability)
  - [Justice interaction matrix](#justice-interaction-matrix)
  - [Constraints](#constraints)
  - [Dynamics](#dynamics)
  - [Welfare](#welfare)
  - [Policy intervention](#policy-intervention)
- [API reference](#api-reference)
- [Examples](#examples)
- [Migration from 0.2.0](#migration-from-020)
- [Repository structure](#repository-structure)
- [Testing](#testing)
- [Citation](#citation)
- [Contributing](#contributing)
- [License](#license)

---

## What's new in 0.3.0

Version 0.3.0 introduces justice as a governance capability. All existing APIs remain backward-compatible.

| Change | Detail |
|---|---|
| **Justice as a sixth capability** | `GovernanceState` now carries a `justice` field (`JusticeState`) alongside `A`, `C`, `S`, `T`, `L` |
| **Five justice dimensions** | Distributive, procedural, recognition, corrective, intergenerational |
| **Three new constraints (C2–C4)** | Justice floor, vulnerability-sensitive non-exploitation, vertical alignment |
| **Justice interaction matrix (M_J)** | Signed matrix capturing synergies and tensions between dimensions |
| **Dimension-specific accountability** | Parent accountability penalized proportional to dimension-specific shortfalls |
| **Dimension-specific prioritarian welfare** | `welfare_dimension_specific` generalizes the scalar form |
| **Policy intervention architecture (new module)** | `PolicyInterventionEnforcer` with cost, horizon, multi-channel capability effects, and recovery |
| **Extended `GSMConfig`** | New fields with sensible defaults; existing fields untouched |
| **Extended metrics** | `justice_index`, `justice_floor_violations`, `exploitation_index`, `justice_misalignment`, `welfare_dimension_specific`, `welfare_components` |
| **New data loaders** | `load_justice_indicators` for empirical calibration |

The architectural change is confined to two existing modules (`core/state.py` and `core/parameters.py`), one new module (`dynamics/enforcement.py`), and additive extensions to the remaining modules. Every v0.2.0 import path continues to work.

---

## Installation

### From PyPI (when published)

```bash
pip install gsm-governance
```

### From source

```bash
git clone https://github.com/hongxueharriswang/gsm-governance.git
cd gsm-governance
pip install -e ".[dev]"
```

### Optional dependencies

```bash
pip install gsm-governance[viz]    # matplotlib for visualization
pip install gsm-governance[data]   # pandas for data loaders
pip install gsm-governance[dev]    # full development stack
```

### Requirements

- Python ≥ 3.9
- NumPy ≥ 1.22
- Optional: matplotlib ≥ 3.5 (visualization), pandas ≥ 1.4 (data)

### Verify installation

```bash
python -m gsm_governance
```

You should see the demonstration output beginning with:

```
========================================================================
GSM-J v0.3.0 — demonstration run
========================================================================
```

---

## Quick start

### A minimal single-jurisdiction model

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState, Simulation,
)

# 1. Configure
config = GSMConfig()

# 2. Build a single-jurisdiction governance system
gov = MultiLevelGovernance(config=config)
gov.add_jurisdiction(
    "Denmark",
    level=4,
    capabilities={"A": 0.82, "C": 0.85, "S": 0.78, "T": 0.75, "L": 0.80},
    justice=JusticeState({
        "distributive": 0.78, "procedural": 0.75,
        "recognition": 0.60, "corrective": 0.35,
        "intergenerational": 0.55,
    }),
)

# 3. Run
sim = Simulation(gov, config=config)
history = sim.run(steps=200)

# 4. Inspect
print(f"Final welfare W*: {history[-1]['W_star']:.4f}")
print(f"Mean justice:     {history[-1]['mean_justice']:.4f}")
```

### A multi-level hierarchy

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState, Simulation,
    justice_step, JusticeInteractionMatrix, MJRegime,
)

config = GSMConfig()
gov = MultiLevelGovernance(config=config)

# National level
gov.add_jurisdiction("national", level=4,
                     capabilities={"A": 0.70, "C": 0.75, "S": 0.60,
                                   "T": 0.65, "L": 0.70})

# Two regions
for rid, recog in [("region_east", 0.55), ("region_west", 0.35)]:
    gov.add_jurisdiction(
        rid, level=3,
        justice=JusticeState({
            "distributive": 0.60, "procedural": 0.55,
            "recognition": recog, "corrective": 0.25,
            "intergenerational": 0.45,
        }),
    )
    gov.link_vertical("national", rid)

gov.link_horizontal("region_east", "region_west")

# Run with a symmetric interaction matrix
sim = Simulation(gov, config=config,
                 M_J=JusticeInteractionMatrix(regime=MJRegime.SYMMETRIC))
history = sim.run(steps=300)
```

### Accessing metrics

```python
from gsm_governance import (
    gsi, hfi, justice_index, justice_floor_violations,
    misalignment, welfare_dimension_specific, welfare_components,
)

print(f"Governance Success Index: {gsi(gov):.4f}")
print(f"Human Flourishing Index:  {hfi(gov):.4f}")
print(f"Justice index:            {justice_index(gov):.4f}")
print(f"Floor violations:         {justice_floor_violations(gov)}")
print(f"Vertical misalignment:    {misalignment(gov):.4f}")

comps = welfare_components(sim.base_welfare(), gov, config)
for k, v in comps.items():
    print(f"  {k}: {v:.4f}")
```

---

## The model

### State vector

Each jurisdiction \( i \) at governance level \( l \in \{1, \dots, L\} \) carries:

\[
\mathbf{x}_i^{(l)}(t) = [A_i, C_i, S_i, T_i, L_i, J_i]
\]

| Symbol | Capability | Range |
|---|---|---|
| \( A_i \) | Accountability | [0, 1] |
| \( C_i \) | Institutional competence | [0, 1] |
| \( S_i \) | Social cohesion | [0, 1] |
| \( T_i \) | Strategic continuity | [0, 1] |
| \( L_i \) | Adaptive learning | [0, 1] |
| \( J_i \) | Justice (5-dimensional) | [0, 1]⁵ |

In code: `GovernanceState` holds the scalar capabilities as attributes (`state.A`, `state.C`, …) and `state.justice` as a `JusticeState`.

### Justice capability

```python
from gsm_governance import JusticeState

j = JusticeState({
    "distributive": 0.65,
    "procedural": 0.55,
    "recognition": 0.30,
    "corrective": 0.20,
    "intergenerational": 0.45,
})

j.aggregate(weights)              # weighted aggregate
j.satisfies_floors(floors)        # bool
j.floor_deficits(floors)          # dict of shortfalls
j.d["distributive"]               # read/write access
j.copy()                          # deep copy
```

Values are clipped to `[0, 1]` on assignment.

### Justice interaction matrix

The signed matrix \( M_J \) captures synergies (positive) and tensions (negative) between justice dimensions.

\[
\mathcal{C}_J^d(\mathbf{J}) = \sum_{e \neq d} m_{de} \, J^e (1 - J^d)
\]

Coefficients are bounded by `m_max` (default 0.30) and can be symmetrized.

```python
from gsm_governance import JusticeInteractionMatrix, MJRegime

# Symmetric regime (10 free parameters) — default
M_sym = JusticeInteractionMatrix(regime=MJRegime.SYMMETRIC)

# Asymmetric regime (20 free parameters)
M_asym = JusticeInteractionMatrix(regime=MJRegime.ASYMMETRIC)

# Custom
M = JusticeInteractionMatrix()
M.m[("procedural", "recognition")] = 0.25       # synergy
M.m[("intergenerational", "distributive")] = -0.15  # tension
```

Default entries encode theoretical priors:

**Synergies:**
- procedural ↔ recognition: +0.15
- distributive ↔ procedural: +0.10
- distributive → corrective: +0.15
- corrective → recognition: +0.20
- recognition → corrective: +0.15
- intergenerational → procedural: +0.05

**Tensions:**
- intergenerational ↔ distributive: −0.05
- corrective → distributive: −0.10
- procedural → intergenerational: −0.05

### Constraints

Four constraints govern the justice subsystem.

| Constraint | Requirement | Checked by |
|---|---|---|
| **C1** | \( E_{ij} \le \tau_j \) or \( \mathrm{Comp}_{ij} \ge E_{ij} \) | `BoundedNonExploitationConstraint` or `ConstraintChecker.C1` |
| **C2** | \( J_i^d \ge J_{\min}^d \) (dimension-specific) | `ConstraintChecker.C2` |
| **C3** | \( J_j < J_{\min}^{\text{agg}} \Rightarrow E_{ij} = 0 \) | `ConstraintChecker.C3` |
| **C4** | \( J_i^{d,(l)} \ge \phi \cdot J_i^{d,(l-1)} \) | `ConstraintChecker.C4` |

```python
from gsm_governance import ConstraintChecker, ExploitationMatrix, CompensationMechanism

checker = ConstraintChecker(gov.config)

# C1: bounded non-exploitation
em = ExploitationMatrix()
em.set("A", "B", {"distributive": 1.0})
cm = CompensationMechanism()
c1_violations = checker.C1(em, cm)

# C2: justice floor
c2_violations = checker.C2(gov.jurisdictions)   # list of (uid, dimension)

# C3: vulnerability-sensitive non-exploitation
c3_violations = checker.C3(em, gov.jurisdictions)   # list of (i, j)

# C4: vertical alignment
c4_violations = checker.C4(gov.jurisdictions)   # list of (uid, dimension_or_'aggregate')

# All at once
all_violations = checker.all(em, cm, gov.jurisdictions)
```

C4 defaults to dimension-level enforcement. Use `GSMConfig(c4_mode=C4Mode.AGGREGATE)` for the aggregate form.

The `BoundedNonExploitationConstraint` class is retained from v0.2.0 with its original signature, for backward compatibility:

```python
from gsm_governance import BoundedNonExploitationConstraint

c = BoundedNonExploitationConstraint(tau=5.0)
# or with per-jurisdiction thresholds
c = BoundedNonExploitationConstraint(tau={"A": 100.0, "B": 5.0})

violations = c.violated_pairs(em, cm)
if c.satisfied(em, cm):
    print("Constraint satisfied")
```

### Dynamics

Justice evolves according to:

\[
\frac{dJ^d}{dt} = g_d(\mathbf{x}) + h_d(\mathbf{E}, \mathrm{Comp}) + \mathcal{C}_J^d(\mathbf{J}) + \eta \sum_j A_{ij}(J_j^d - J_i^d) - \kappa_d J_i^d
\]

- **Internal coupling** \( g_d \) — justice dimensions supported by base capabilities
- **Exploitation/compensation** \( h_d \) — exploitation erodes justice; compensation restores it
- **Corrective restorative** — remedy builds restorative capability
- **Horizontal diffusion** — justice diffuses across neighbours
- **Decay** — per-dimension decay

```python
from gsm_governance import (
    justice_step, base_capability_step,
    update_accountability_dimension_specific,
)

# Advance one jurisdiction's justice state by dt
justice_step(jurisdiction, governance, exploitation, compensation,
             config, M_J, dt=0.05)

# Advance base capabilities
base_capability_step(jurisdiction, governance, config, dt=0.05)

# Update cross-level accountability (dimension-specific)
update_accountability_dimension_specific(parent, governance, config)
```

These functions are called internally by `Simulation.step()`; they are exposed for custom dynamics.

### Welfare

Dimension-specific prioritarian welfare:

\[
W^* = W + \sum_d \gamma_d J^d - \sum_d \delta_d [J_{\min}^d - J^d]^+
\]

Default condition \( \delta_d > \gamma_d \) implements prioritarianism: justice deficits reduce welfare at a rate exceeding the symmetric contribution.

```python
from gsm_governance import (
    welfare, welfare_dimension_specific, welfare_components,
)

# Scalar form (backward-compatible)
w = welfare(gov, base_welfare=1.0)

# Dimension-specific form
w_star = welfare_dimension_specific(1.0, gov, config)

# Component breakdown
comps = welfare_components(1.0, gov, config)
# {'base': 1.0,
#  'justice_contribution': 2.8,
#  'prioritarian_penalty': -0.5,
#  'W_star': 3.3}
```

### Policy intervention

Constraint enforcement via projection is reframed as policy intervention with four attributes:

1. **Designated authority** — who implements the correction
2. **Implementation cost** \( \kappa^{\text{int}} \) per unit of correction
3. **Finite effective horizon** \( \tau^{\text{int}} \) (steps to full implementation)
4. **Multi-channel capability effects** — cost distributed across competence, cohesion, continuity, and accountability

```python
from gsm_governance import (
    PolicyInterventionEnforcer, GSMConfig,
)

config = GSMConfig(
    intervention_cost=0.10,
    intervention_horizon=5,
    intervention_weights={"C": 0.50, "S": 0.25, "T": 0.15, "A": 0.10},
    recovery={"C": 0.05, "S": 0.05, "T": 0.05, "A": 0.05},
)

enforcer = PolicyInterventionEnforcer(config)

# Manual stepping
enforcer.check_and_schedule(gov, exploitation)
enforcer.apply_step(gov, exploitation)
enforcer.apply_recovery(gov)

# Or in one call
enforcer.enforce(gov, exploitation)

# Statistics
print(enforcer.active_count)     # currently active interventions
print(enforcer.stats)            # {'scheduled': 42, 'completed': 40, 'total_cost': 3.28}
```

**Frequency ceiling.** Because interventions consume capability, aggressive justice improvement is self-limiting. Under single-channel cost (only `C`), interventions can be sustained at high frequency. Under multi-channel cost (default), cohesion and continuity degrade, capping the total intervention rate.

---

## API reference

### Parameters

| Class | Purpose |
|---|---|
| `GSMConfig` | Full parameter set (structural + normative) |
| `JusticeInteractionMatrix` | Signed interaction matrix \( M_J \) |
| `C4Mode` | Enum: `PER_DIMENSION`, `AGGREGATE`, `HYBRID` |
| `MJRegime` | Enum: `SYMMETRIC`, `ASYMMETRIC` |
| `EnforcementMode` | Enum: `PROJECTION`, `REVERSAL`, `HYBRID` |

### Constants

```python
from gsm_governance import (
    JUSTICE_DIMENSIONS,      # ('distributive', 'procedural', 'recognition',
                             #  'corrective', 'intergenerational')
    BASE_CAPABILITIES,       # ('A', 'C', 'S', 'T', 'L')
    INTERVENTION_CHANNELS,   # ('C', 'S', 'T', 'A')
)
```

### State objects

| Class | Purpose |
|---|---|
| `JusticeState` | Five-dimensional justice capability |
| `GovernanceState` | Full state vector (base capabilities + justice) |
| `FlourishingState` | Base flourishing indicators |
| `CompensationVector` | Six-component compensation vector |
| `ExploitationMatrix` | Tracks \( E_{ij} \) decomposed by dimension |
| `CompensationMechanism` | Tracks \( \mathrm{Comp}_{ij} \) mapped to dimensions |

### System objects

| Class | Purpose |
|---|---|
| `Jurisdiction` | A governance unit (uid, level, state, links) |
| `MultiLevelGovernance` | Container managing the hierarchy |

`MultiLevelGovernance` methods:

```python
gov = MultiLevelGovernance(config=config)
gov.add_jurisdiction(uid, level, capabilities=None, justice=None)
gov.remove_jurisdiction(uid)
gov.link_vertical(parent, child)
gov.link_horizontal(a, b)
gov[uid]                    # lookup
len(gov)                    # count
uid in gov                  # membership
for j in gov: ...           # iteration
gov.by_level(level)         # filter
gov.levels()                # list of levels
gov.roots()                 # top-level jurisdictions
gov.aggregate_justice()     # mean aggregate justice
```

### Constraints

| Class | Purpose |
|---|---|
| `BoundedNonExploitationConstraint` | C1 (backward-compatible) |
| `JusticeConstraintSet` | Full C1–C4 set |
| `ConstraintChecker` | Unified interface |

`ConstraintChecker` methods:

```python
checker = ConstraintChecker(config)
checker.C1(exploitation, compensation)
checker.C2(jurisdictions)
checker.C3(exploitation, jurisdictions)
checker.C4(jurisdictions)
checker.all(exploitation, compensation, jurisdictions)
```

### Enforcement

```python
enforcer = PolicyInterventionEnforcer(config, mode=None)
enforcer.check_and_schedule(gov, exploitation)
enforcer.apply_step(gov, exploitation)
enforcer.apply_recovery(gov)
enforcer.enforce(gov, exploitation)
enforcer.reset()
enforcer.active           # list of active interventions
enforcer.active_count     # int
enforcer.stats            # {'scheduled', 'completed', 'total_cost'}
```

### Simulation

```python
sim = Simulation(
    governance,             # MultiLevelGovernance
    config=None,            # defaults to governance.config
    M_J=None,               # defaults to symmetric default matrix
    constraint=None,        # optional custom C1 constraint
    enforcer=None,          # optional custom enforcer
    seed=None,              # optional RNG seed
)

sim.set_exploitation(i, j, values)
sim.set_compensation(i, j, values)
sim.base_welfare()          # scalar
sim.welfare()               # scalar W*
sim.step()                  # advance one step
sim.record()                # append to history
sim.run(steps=500)          # step + record loop
sim.reset()                 # clear history
sim.history                 # list of records
```

Each history record contains:

```python
{
    "t": 25.0,
    "W_star": 3.4821,
    "mean_justice": 0.5104,
    "dim_means": {"distributive": 0.62, ...},
    "C1_violations": 0,
    "C2_violations": 0,
    "C3_violations": 0,
    "C4_violations": 0,
    "active_interventions": 0,
    "total_cost": 2.7413,
}
```

### Dynamics functions

```python
justice_step(j, governance, exploitation, compensation, config, M_J, dt)
base_capability_step(j, governance, config, dt)
update_accountability_dimension_specific(parent, governance, config)
```

### Metrics

```python
from gsm_governance import (
    # Composite indices
    gsi, hfi, justice_index,
    # Violation and exploitation
    justice_floor_violations, exploitation_index,
    # Misalignment and resilience
    misalignment, justice_misalignment, resilience,
    # Welfare
    welfare, welfare_dimension_specific, welfare_components,
)
```

### Utilities

```python
from gsm_governance import min_max_normalize, z_score_normalize
from gsm_governance.utils.visualization import (
    plot_welfare, plot_dimension_trajectories, plot_interventions,
    plot_justice_radar,
)
```

### Data loaders

```python
from gsm_governance.data import (
    load_denmark_raw,       # stylized demo data
    normalize_denmark,
    load_justice_indicators,
    SOURCES, source_metadata,
)
```

---

## Examples

### Example 1 — Single jurisdiction, no interventions

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState, Simulation,
)

config = GSMConfig()
gov = MultiLevelGovernance(config=config)
gov.add_jurisdiction(
    "X", level=4,
    capabilities={"A": 0.8, "C": 0.8, "S": 0.7, "T": 0.7, "L": 0.75},
    justice=JusticeState({d: 0.7 for d in [
        "distributive", "procedural", "recognition",
        "corrective", "intergenerational",
    ]}),
)

sim = Simulation(gov, config=config)
history = sim.run(steps=200)
print(f"W* = {history[-1]['W_star']:.4f}")
```

### Example 2 — Multi-level hierarchy with exploitation

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState, Simulation,
)

config = GSMConfig()
gov = MultiLevelGovernance(config=config)

gov.add_jurisdiction("national", level=4)
gov.add_jurisdiction(
    "region", level=3,
    justice=JusticeState({"distributive": 0.65, "procedural": 0.60,
                          "recognition": 0.30, "corrective": 0.20,
                          "intergenerational": 0.45}),
)
gov.add_jurisdiction(
    "community", level=2,
    justice=JusticeState({"distributive": 0.50, "procedural": 0.45,
                          "recognition": 0.20, "corrective": 0.15,
                          "intergenerational": 0.35}),
)

gov.link_vertical("national", "region")
gov.link_vertical("region", "community")

sim = Simulation(gov, config=config)

# Region exploits community without full compensation
sim.set_exploitation("region", "community", {
    "distributive": 0.20, "procedural": 0.10, "recognition": 0.15,
    "corrective": 0.00, "intergenerational": 0.10,
})
sim.set_compensation("region", "community", {
    "distributive": 0.10, "procedural": 0.02, "recognition": 0.00,
    "corrective": 0.00, "intergenerational": 0.03,
})

history = sim.run(steps=400)

print(f"Final W*: {history[-1]['W_star']:.4f}")
print(f"C3 violations: {history[-1]['C3_violations']}")
print(f"Interventions: {history[-1]['active_interventions']}")
```

### Example 3 — Comparing single- and multi-channel intervention cost

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState, Simulation,
)

def build(config):
    gov = MultiLevelGovernance(config=config)
    gov.add_jurisdiction("P", level=3)
    gov.add_jurisdiction(
        "C", level=2,
        justice=JusticeState({"distributive": 0.05, "procedural": 0.05,
                              "recognition": 0.05, "corrective": 0.05,
                              "intergenerational": 0.05}),
    )
    gov.link_vertical("P", "C")
    return gov

for label, weights in (
    ("single-channel", {"C": 1.0, "S": 0.0, "T": 0.0, "A": 0.0}),
    ("multi-channel",  {"C": 0.50, "S": 0.25, "T": 0.15, "A": 0.10}),
):
    config = GSMConfig(intervention_weights=weights)
    gov = build(config)
    sim = Simulation(gov, config=config)
    history = sim.run(steps=400)
    print(f"{label:14s}  W* = {history[-1]['W_star']:.4f}  "
          f"interventions = {history[-1]['total_cost']:.4f}")
```

Under multi-channel costs, the frequency ceiling emerges: cohesion and continuity deplete, reducing the enforcer's capacity to schedule further interventions.

### Example 4 — Visualizing a run

```python
from gsm_governance.utils.visualization import (
    plot_welfare, plot_dimension_trajectories, plot_justice_radar,
)

plot_welfare(history, save_path="welfare.png")
plot_dimension_trajectories(history, save_path="dimensions.png")
plot_justice_radar(gov, uids=["national", "region", "community"],
                   save_path="radar.png")
```

### Example 5 — Custom dynamics

```python
from gsm_governance import Simulation

class ShockSimulation(Simulation):
    """Applies a distributive shock at t=10."""
    def __init__(self, *args, shock_time=10.0, shock_size=0.3, **kwargs):
        super().__init__(*args, **kwargs)
        self.shock_time = shock_time
        self.shock_size = shock_size
        self._applied = False

    def step(self):
        super().step()
        if not self._applied and self.t >= self.shock_time:
            for j in self.governance.jurisdictions.values():
                cur = j.state.justice.d["distributive"]
                j.state.justice.d["distributive"] = max(0.0, cur - self.shock_size)
            self._applied = True

sim = ShockSimulation(gov, config=config)
history = sim.run(steps=300)
```

---

## Migration from 0.2.0

All v0.2.0 APIs continue to work. The changes are additive.

| v0.2.0 usage | v0.3.0 status |
|---|---|
| `MultiLevelGovernance(config=...)` | Unchanged |
| `gov.add_jurisdiction(uid, level)` | Unchanged; now also accepts `capabilities` and `justice` |
| `gov.link_vertical(p, c)`, `gov.link_horizontal(a, b)` | Unchanged |
| `Jurisdiction.state` with `A`, `C`, `S`, `T`, `L` | Unchanged; `state.justice` added |
| `GSMConfig(...)` existing fields | Unchanged; new fields have defaults |
| `BoundedNonExploitationConstraint(tau, valuation_vectors)` | Unchanged |
| `Simulation(system, constraint, seed).run(...)` | Unchanged; extra args optional |
| `gsi(gov)`, `hfi(gov)` | Now module-level functions (were methods) |
| `CompensationVector` (six components) | Unchanged; `to_justice_dimensions()` added |
| `welfare(gov)` | Unchanged; new `welfare_dimension_specific` and `welfare_components` available |
| `misalignment(gov)`, `resilience(history, t)` | Unchanged |

**Breaking changes.** None.

**Deprecated names.** None.

**New names to migrate towards.** For new code, prefer:

- `ConstraintChecker(config)` over direct `BoundedNonExploitationConstraint` construction, to get access to C1–C4 uniformly.
- `PolicyInterventionEnforcer(config)` for constraint enforcement instead of ad-hoc projection logic.
- `welfare_dimension_specific(...)` instead of `welfare(...)` when dimension-specific weighting is desired.

---

## Repository structure

```
gsm-governance/
├── README.md
├── LICENSE
├── pyproject.toml
├── gsm_governance/
│   ├── __init__.py           # public API
│   ├── __main__.py           # demonstration entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── parameters.py     # GSMConfig, JusticeInteractionMatrix, enums
│   │   ├── state.py          # GovernanceState, JusticeState, ExploitationMatrix, ...
│   │   └── system.py         # Jurisdiction, MultiLevelGovernance
│   ├── dynamics/
│   │   ├── __init__.py
│   │   ├── constraint.py     # BoundedNonExploitationConstraint, JusticeConstraintSet, ConstraintChecker
│   │   ├── enforcement.py    # PolicyInterventionEnforcer  (NEW in 0.3.0)
│   │   ├── simulation.py     # Simulation
│   │   └── transitions.py    # justice_step, base_capability_step, accountability
│   ├── metrics/
│   │   ├── __init__.py
│   │   ├── indices.py        # gsi, hfi, justice_index, ...
│   │   ├── misalignment.py   # misalignment, justice_misalignment
│   │   ├── resilience.py     # resilience
│   │   └── welfare.py        # welfare, welfare_dimension_specific, welfare_components
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loaders.py        # load_denmark_raw, normalize_denmark, load_justice_indicators
│   │   └── sources.py        # SOURCES, source_metadata
│   └── utils/
│       ├── __init__.py
│       ├── normalization.py  # min_max_normalize, z_score_normalize
│       └── visualization.py  # plot_welfare, plot_justice_radar, ...
└── tests/
    ├── test_gsm.py
    └── ...
```

---

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=gsm_governance --cov-report=term-missing
```

The test suite covers:

- All state classes (`JusticeState`, `GovernanceState`, `CompensationVector`, `ExploitationMatrix`)
- Parameter validation (`GSMConfig`, `JusticeInteractionMatrix`)
- Constraint detection (C1–C4, per-dimension and aggregate C4)
- Enforcement scheduling, cost charging, and recovery
- Dynamics (`justice_step`, `base_capability_step`, accountability)
- Welfare computation and prioritarian penalty behavior
- Metrics (indices, misalignment, exploitation)
- End-to-end simulation determinism and convergence

Tests are deterministic. The library contains no stochastic elements by default; the optional `seed` argument to `Simulation` enables reproducible randomization for future extensions.

---

## Citation

If you use this library in academic work, please cite the manuscript and the software.

**Manuscript:**

```bibtex
@misc{wang2026gsmj,
  title  = {Justice as a Governance Capability: A Computational Systems Model
            of Multi-Level Governance for Human Flourishing under
            Bounded Non-Exploitation},
  author = {Wang, Harris},
  year   = {2026},
  doi    = {10.20944/preprints202609.0964.v2},
  note   = {Preprint}
}
```

**Software:**

```bibtex
@software{gsmgovernance2026,
  title   = {gsm-governance: Reference implementation of GSM-J},
  author  = {Wang, Harris},
  year    = {2026},
  url     = {https://github.com/hongxueharriswang/gsm-governance},
  version = {0.3.0}
}
```

---

## Contributing

Contributions are welcome. Areas of particular interest:

- **Empirical calibration** of \( M_J \) from panel data (manuscript Appendix D)
- **Alternative intervention cost models** (nonlinear, network effects)
- **Additional justice dimensions** with theoretical justification
- **Visualization tools** for justice trajectories and intervention schedules
- **Case study applications** using real governance data
- **Documentation** including tutorials and worked examples

### Development workflow

```bash
git clone https://github.com/hongxueharriswang/gsm-governance.git
cd gsm-governance
pip install -e ".[dev]"

pytest tests/
ruff check gsm_governance/
black --check gsm_governance/
```

### Code style

- PEP 8 compliant (`black`, line length 88)
- Type hints required for public functions
- Docstrings required for public classes and functions
- Tests required for new functionality

### Reporting issues

Please use the GitHub issue tracker with:

- Reproduction steps
- Expected vs. observed behavior
- Environment (Python version, OS)
- If applicable, the parameter configuration

---

## License

Released under the MIT License. See [LICENSE](LICENSE).

---

## Roadmap

| Version | Focus |
|---|---|
| **0.2.0** | Baseline GSM, bounded non-exploitation, compensation, single-level hierarchy |
| **0.3.0** | **Justice as a governance capability (GSM-J): five dimensions, four constraints, M_J, dimension-specific accountability and welfare, policy intervention enforcement** |
| 0.4.0 | Empirical calibration utilities (Bayesian hierarchical estimation of M_J) |
| 0.5.0 | Full exploitation index operationalization from external data |
| 0.6.0 | Comparative case-study applications (Denmark, EU, global governance) |
| 1.0.0 | Stable API; documented normative-parameter conventions |

---

**Status:** v0.3.0 — matches manuscript v8. Architecture is complete; the next phase is empirical calibration.