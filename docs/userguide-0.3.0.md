# gsm-governance User Guide

**A comprehensive guide to simulating justice-augmented multi-level governance**

Version 0.3.0 · Companion to the GSM-J preprint

---

## Table of contents

**Part I — Getting started**
1. [What this library does](#1-what-this-library-does)
2. [Installation and verification](#2-installation-and-verification)
3. [Your first simulation](#3-your-first-simulation)
4. [GSM-J 0.3.0 as a superset of GSM 0.2.0](#4-gsm-j-030-as-a-superset-of-gsm-020)

**Part II — Core concepts**
5. [Jurisdictions and levels](#5-jurisdictions-and-levels)
6. [Capabilities and justice](#6-capabilities-and-justice)
7. [The justice interaction matrix](#7-the-justice-interaction-matrix)
8. [Constraints](#8-constraints)
9. [Welfare](#9-welfare)
10. [Interventions](#10-interventions)

**Part III — Building models**
11. [Building a hierarchy from scratch](#11-building-a-hierarchy-from-scratch)
12. [Injecting exploitation and compensation](#12-injecting-exploitation-and-compensation)
13. [Configuring normative parameters](#13-configuring-normative-parameters)
14. [Configuring structural parameters](#14-configuring-structural-parameters)

**Part IV — Running experiments**
15. [Running and inspecting simulations](#15-running-and-inspecting-simulations)
16. [Scenario comparisons](#16-scenario-comparisons)
17. [Sensitivity analysis](#17-sensitivity-analysis)
18. [Visualization](#18-visualization)

**Part V — Advanced usage**
19. [Custom dynamics](#19-custom-dynamics)
20. [Custom enforcement](#20-custom-enforcement)
21. [Empirical calibration of M_J](#21-empirical-calibration-of-m_j)
22. [Extending the justice dimensions](#22-extending-the-justice-dimensions)

**Part VI — Reference**
23. [Common patterns and recipes](#23-common-patterns-and-recipes)
24. [Troubleshooting](#24-troubleshooting)
25. [Glossary](#25-glossary)

---

# Part I — Getting started

## 1. What this library does

`gsm-governance` simulates multi-level governance systems in which justice is a **capability** — a state variable that co-evolves with accountability, competence, cohesion, continuity, and learning — rather than an external evaluative constraint.

You can use it to:

- **Model governance hierarchies** with arbitrary numbers of levels, jurisdictions, and links.
- **Simulate justice dynamics** across five dimensions: distributive, procedural, recognition, corrective, intergenerational.
- **Explore normative trade-offs** by varying weights, floors, and prioritarian penalties.
- **Test intervention schedules** and observe capability costs, delays, and frequency ceilings.
- **Compare scenarios** like universal floors vs. no floors, or single-channel vs. multi-channel intervention cost.
- **Investigate structural questions** about multi-level governance under bounded non-exploitation.

The library is **conditional**: it does not decide what is just. You supply the normative parameters; the model predicts systemic consequences.

---

## 2. Installation and verification

### Requirements

- Python 3.9 or later
- NumPy 1.22 or later
- Optional: `matplotlib` (visualization), `pandas` (data loaders)

### Install from source

```bash
git clone https://github.com/hongxueharriswang/gsm-governance.git
cd gsm-governance
pip install -e ".[dev]"
```

### Optional extras

```bash
pip install -e ".[viz]"     # matplotlib for visualization
pip install -e ".[data]"    # pandas for data loaders
pip install -e ".[dev]"     # full development stack
```

### Verify installation

```python
import gsm_governance as gsm
print(gsm.__version__)
# "0.3.0"
```

### Run the built-in demonstration

```bash
python -m gsm_governance
```

This runs a default simulation, prints a per-jurisdiction profile, and compares single-channel vs. multi-channel intervention costs. You should see:

```
========================================================================
GSM-J v0.3.0 — demonstration run
========================================================================
```

If you see this output, the installation is working.

---

## 3. Your first simulation

### A minimal single-jurisdiction model

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState, Simulation,
)

# 1. Configure
config = GSMConfig()

# 2. Build a governance system
gov = MultiLevelGovernance(config=config)
gov.add_jurisdiction(
    "Denmark",
    level=4,
    capabilities={"A": 0.82, "C": 0.85, "S": 0.78, "T": 0.75, "L": 0.80},
    justice=JusticeState({
        "distributive": 0.78,
        "procedural": 0.75,
        "recognition": 0.60,
        "corrective": 0.35,
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

**What just happened.** At each time step:

1. Base capabilities drifted toward targets determined by the justice profile.
2. Justice dimensions evolved via internal coupling, exploitation/compensation, diffusion, and decay.
3. Cross-level accountability was updated (dimension-specific).
4. Justice suppressed exploitation.
5. The policy intervention enforcer scheduled and applied corrective interventions where floors or vertical alignment were violated.

### A multi-level hierarchy

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState, Simulation,
    JusticeInteractionMatrix, MJRegime,
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

---

## 4. GSM-J 0.3.0 as a superset of GSM 0.2.0

**GSM-J 0.3.0 is a strict superset of GSM 0.2.0.** Every v0.2.0 import path, class, and function is preserved. The 0.3.0 additions are entirely additive; no existing API was renamed, removed, or changed in behavior in a breaking way.

### What "superset" means concretely

| Aspect | GSM 0.2.0 | GSM-J 0.3.0 |
|---|---|---|
| **State vector** | `[A, C, S, T, L]` | `[A, C, S, T, L, J]` — justice added as a sixth capability |
| **Constraints** | C1 (bounded non-exploitation) | C1 + C2 + C3 + C4 |
| **Welfare** | Scalar `welfare(gov)` | Scalar `welfare(gov)` (unchanged) **plus** `welfare_dimension_specific(...)` and `welfare_components(...)` |
| **Enforcement** | Ad-hoc projection in the simulation loop | Formal `PolicyInterventionEnforcer` with cost, horizon, multi-channel effects, and recovery |
| **Metrics** | `gsi`, `hfi`, `misalignment`, `resilience` | All retained, plus `justice_index`, `justice_floor_violations`, `exploitation_index`, `justice_misalignment` |
| **Config** | `GSMConfig` with structural + basic normative fields | All v0.2.0 fields unchanged; new justice fields added with defaults |

### Backward-compatibility evidence

Every v0.2.0 import continues to work:

```python
# v0.2.0 imports — all still valid
from gsm_governance import (
    MultiLevelGovernance,
    GSMConfig,
    BoundedNonExploitationConstraint,
    CompensationVector,
    Simulation,
    gsi, hfi, misalignment, resilience, welfare,
)

# v0.2.0-style construction — still works
gov = MultiLevelGovernance.from_single_jurisdiction("X", level=4)
c = BoundedNonExploitationConstraint(tau=5.0)
sim = Simulation(gov, seed=42)
history = sim.run(steps=100)
```

### What changed under the hood (without breaking anything)

1. **`MultiLevelGovernance`** now internally carries a `JusticeState` per jurisdiction. If you never initialize it, it defaults to `0.5` on every dimension. This is why v0.2.0 code runs unchanged: the model simply operates on the default justice profile (which, under the default floors, will trigger interventions that were absent in v0.2.0).

2. **`gsi` and `hfi`** were methods in v0.2.0 and are now module-level functions. This was made backward-compatible via a shim: `MultiLevelGovernance.gsi()` and `.hfi()` still work. New code should prefer `gsi(gov)` and `hfi(gov)`.

3. **`GSMConfig`** gained new fields (`justice_weights`, `justice_floors`, `intervention_cost`, etc.). All have defaults. Validation runs automatically; existing configurations validate as long as the new defaults are consistent with the existing parameters.

### Enabling the full GSM-J behavior on a v0.2.0 model

If you have a v0.2.0 model and want to benefit from the justice extensions:

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState, Simulation,
)

config = GSMConfig()

# Build a v0.2.0-style hierarchy
gov = MultiLevelGovernance(config=config)
gov.add_jurisdiction("X", level=4)

# Inject a justice profile
gov["X"].state.justice = JusticeState({
    "distributive": 0.65,
    "procedural": 0.55,
    "recognition": 0.30,
    "corrective": 0.20,
    "intergenerational": 0.45,
})

sim = Simulation(gov, config=config)
history = sim.run(steps=300)
```

### Why the superset design matters

- **Reproducibility:** any result produced with 0.2.0 can be reproduced with 0.3.0.
- **Migration is optional:** new users can start with justice; existing users can adopt the extensions incrementally.
- **Scientific comparability:** results across versions are directly comparable when justice parameters are held at defaults.

---

# Part II — Core concepts

## 5. Jurisdictions and levels

A **jurisdiction** is any governance unit: a household, a neighborhood, a municipality, a national government, a regional bloc, or a global body. Each jurisdiction belongs to a **level**, an integer index.

The convention in GSM-J is:

| Level | Representative unit |
|---|---|
| 1 | Household / individual |
| 2 | Community |
| 3 | Subnational |
| 4 | National |
| 5 | Regional |
| 6 | Global |

Levels are just labels. You can use any integer scheme that makes sense for your model.

### Creating jurisdictions

```python
from gsm_governance import MultiLevelGovernance, GSMConfig, JusticeState

gov = MultiLevelGovernance(config=GSMConfig())

# Minimal jurisdiction (defaults to all capabilities = 0.5)
gov.add_jurisdiction("municipality_A", level=3)

# With custom capabilities and justice profile
gov.add_jurisdiction(
    "municipality_B",
    level=3,
    capabilities={"A": 0.65, "C": 0.70, "S": 0.55, "T": 0.50, "L": 0.60},
    justice=JusticeState({
        "distributive": 0.65,
        "procedural": 0.55,
        "recognition": 0.30,
        "corrective": 0.20,
        "intergenerational": 0.45,
    }),
)
```

### Linking jurisdictions

**Vertical links** establish parent-child relationships between levels:

```python
gov.link_vertical("national_government", "municipality_A")
```

**Horizontal links** establish neighbour relationships within a level:

```python
gov.link_horizontal("municipality_A", "municipality_B")
```

Horizontal links matter because justice diffuses across neighbours (parameter `η`). Vertical links matter because:

1. Higher levels are **accountable** for justice delivered at lower levels.
2. Higher levels may not **erode** justice achieved at lower levels (constraint C4).
3. Interventions that correct lower-level justice shortfalls may be charged to the parent as the designated authority.

### Inspecting the hierarchy

```python
for uid, j in gov.jurisdictions.items():
    print(f"{uid} (level {j.level})")
    print(f"  parent    : {j.parent}")
    print(f"  children  : {j.children}")
    print(f"  neighbours: {j.neighbours}")
```

### Hierarchy accessors

```python
gov["national"]           # lookup by uid
"national" in gov         # membership test
len(gov)                  # number of jurisdictions
gov.levels()              # sorted list of levels
gov.by_level(3)           # list of jurisdictions at level 3
gov.roots()               # top-level jurisdictions (no parent)
gov.aggregate_justice()   # mean aggregate justice across all jurisdictions
```

---

## 6. Capabilities and justice

Each jurisdiction has two state components:

- **Base capabilities** — `A`, `C`, `S`, `T`, `L`
- **Justice** — a `JusticeState` with five dimensions

### Reading and writing capabilities

```python
j = gov.jurisdictions["municipality_A"]

# Read
print(j.state.A)    # accountability
print(j.state.C)    # competence
print(j.state.S)    # cohesion
print(j.state.T)    # continuity
print(j.state.L)    # learning

# Write
j.state.A = 0.75
```

### Reading and writing justice

```python
# Read individual dimensions
print(j.state.justice.d["distributive"])       # 0.65
print(j.state.justice.d["procedural"])         # 0.55
print(j.state.justice.d["recognition"])        # 0.30
print(j.state.justice.d["corrective"])         # 0.20
print(j.state.justice.d["intergenerational"])  # 0.45

# Or use dict-style access
print(j.state.justice["distributive"])         # 0.65
j.state.justice["distributive"] = 0.80         # clips to [0, 1]

# Weighted aggregate
print(j.state.justice.aggregate(config.justice_weights))

# Floor checks
print(j.state.justice.satisfies_floors(config.justice_floors))   # bool
print(j.state.justice.floor_deficits(config.justice_floors))     # dict
```

### Why justice is a state variable

In conventional governance models, justice is an **external criterion**: you compute some outcome and then ask whether it is just. In GSM-J, justice is a **state variable**: it evolves over time, is affected by other capabilities, and affects them in turn.

This matters for at least three reasons:

1. **Feedback loops.** Justice deficits reduce other capabilities (e.g., weak procedural justice slows learning), which in turn slow justice improvement.
2. **Temporal dynamics.** A jurisdiction's justice trajectory depends on its history, not just its current policies.
3. **Intervention realism.** Correcting a justice deficit consumes capabilities, so justice improvement is not free.

### `JusticeState` API

```python
from gsm_governance import JusticeState

j = JusticeState({
    "distributive": 0.65,
    "procedural": 0.55,
    "recognition": 0.30,
    "corrective": 0.20,
    "intergenerational": 0.45,
})

j.d                      # dict of dimension -> value
j["distributive"]        # 0.65
j["distributive"] = 0.9  # set (clipped to [0, 1])
j.aggregate(weights)     # float
j.satisfies_floors(floors)   # bool
j.floor_deficits(floors)     # dict of deficits
j.copy()                 # deep copy
j.as_dict()              # dict copy
```

All values are clipped to `[0, 1]` on assignment. Unknown dimension keys raise `KeyError`.

---

## 7. The justice interaction matrix

Justice dimensions interact. Some reinforce each other (procedural justice enables recognition justice); others trade off (intergenerational investment displaces present distribution). The interaction matrix `M_J` captures both.

### Default matrix

```python
from gsm_governance import JusticeInteractionMatrix, MJRegime

M = JusticeInteractionMatrix(regime=MJRegime.SYMMETRIC)

for (src, tgt), coef in sorted(M.m.items()):
    print(f"{src:20s} -> {tgt:20s} : {coef:+.3f}")
```

Default synergies:

| Source | Target | Coefficient |
|---|---|---|
| procedural | recognition | +0.15 |
| recognition | procedural | +0.15 |
| distributive | procedural | +0.10 |
| procedural | distributive | +0.10 |
| distributive | corrective | +0.15 |
| corrective | recognition | +0.20 |
| recognition | corrective | +0.15 |
| intergenerational | procedural | +0.05 |

Default tensions:

| Source | Target | Coefficient |
|---|---|---|
| intergenerational | distributive | −0.05 |
| distributive | intergenerational | −0.05 |
| corrective | distributive | −0.10 |
| procedural | intergenerational | −0.05 |

### Why both signs matter

Under a purely positive matrix, justice dimensions reinforce each other monotonically: investing in one dimension lifts others. This produces unrealistically optimistic projections.

Under a signed matrix, trade-offs appear:

- **Recognition improvement** may temporarily reduce distributive flexibility.
- **Intergenerational investment** may slow present distribution.
- **Large corrective transfers** may draw from current distributive resources.

In ablation studies, disabling negative entries produces higher aggregate justice but **lower** long-run welfare, because the system over-invests in single dimensions.

### Setting a custom matrix

```python
M = JusticeInteractionMatrix()
M.m = {
    ("procedural", "recognition"):        +0.20,
    ("recognition", "procedural"):        +0.20,
    ("intergenerational", "distributive"): -0.15,
    ("distributive", "intergenerational"): -0.15,
    # ... etc.
}
M.symmetrize()   # enforce symmetry prior
```

### Symmetric vs. asymmetric regimes

- **Symmetric** (`m_de = m_ed`): 10 free parameters, appropriate for small samples.
- **Asymmetric** (`m_de ≠ m_ed`): 20 free parameters, appropriate when directional hypotheses are of interest.

```python
M_sym = JusticeInteractionMatrix(regime=MJRegime.SYMMETRIC)
M_asym = JusticeInteractionMatrix(regime=MJRegime.ASYMMETRIC)
```

### Bounds

Every coefficient is clipped to `[-m_max, +m_max]` (default `m_max = 0.30`) inside `coupling()`:

```python
M = JusticeInteractionMatrix()
M.m[("procedural", "recognition")] = 5.0   # set extremely large
# Internally clipped to 0.30 when computing coupling
```

### Passing a matrix to a simulation

```python
from gsm_governance import Simulation

sim = Simulation(gov, config=config, M_J=M)
```

If `M_J` is not supplied, the simulation uses the default symmetric matrix.

---

## 8. Constraints

Four constraints govern the justice subsystem. Each is checked at every step and enforced via policy intervention when applicable.

### C1 — Bounded non-exploitation

\[
E_{ij} \le \tau_j \quad \text{or} \quad \mathrm{Comp}_{ij} \ge E_{ij}
\]

Exploitation is permitted below a tolerance threshold, or above it if adequately compensated.

```python
from gsm_governance import (
    ConstraintChecker, ExploitationMatrix, CompensationMechanism,
    BoundedNonExploitationConstraint,
)

checker = ConstraintChecker(config)

em = ExploitationMatrix()
em.set("A", "B", {"distributive": 10.0})

cm = CompensationMechanism()
cm.set("A", "B", {"distributive": 0.0})

violations = checker.C1(em, cm)
print(f"C1 violations: {violations}")   # [('A', 'B')]
```

The `BoundedNonExploitationConstraint` class is retained with its original v0.2.0 signature:

```python
c = BoundedNonExploitationConstraint(tau=5.0)
# or with per-jurisdiction thresholds
c = BoundedNonExploitationConstraint(tau={"A": 100.0, "B": 5.0})

if c.satisfied(em, cm):
    print("Constraint satisfied")

violations = c.violated_pairs(em, cm)
```

### C2 — Justice floor

\[
J_i^d \ge J_{\min}^d
\]

No jurisdiction may fall below the dimension-specific floor.

```python
violations = checker.C2(gov.jurisdictions)
for uid, dim in violations:
    print(f"{uid} is below the {dim} floor")
```

Floor values are supplied in `config.justice_floors`:

```python
config.justice_floors = {
    "distributive": 0.30,
    "procedural": 0.25,
    "recognition": 0.25,
    "corrective": 0.10,
    "intergenerational": 0.20,
}
```

### C3 — Vulnerability-sensitive non-exploitation

If a jurisdiction falls below the aggregate floor, no exploitation of it is permitted regardless of compensation.

```python
violations = checker.C3(em, gov.jurisdictions)
```

This is the most distinctive normative constraint in GSM-J. It encodes a **prioritarian** commitment: the worse off a jurisdiction is, the stronger its protection against further extraction.

### C4 — Vertical justice alignment (subsidiarity)

Higher levels may not erode justice achieved at lower levels. By default, this is enforced **per dimension**:

\[
J_i^{d,(l)} \ge \phi \cdot J_i^{d,(l-1)}
\]

```python
violations = checker.C4(gov.jurisdictions)
```

To use the aggregate formulation instead:

```python
from gsm_governance import C4Mode, GSMConfig

config = GSMConfig(c4_mode=C4Mode.AGGREGATE)
checker = ConstraintChecker(config)
```

### Checking all constraints at once

```python
violations = checker.all(em, cm, gov.jurisdictions)
# {'C1': [...], 'C2': [...], 'C3': [...], 'C4': [...]}
```

### Interpreting violation counts

Under the default hybrid enforcement mode, violations are **detected, then corrected via intervention** over a finite horizon. The number of violations at any step reflects:

- How recently the violation appeared
- Whether the designated authority has sufficient capability
- Whether the intervention horizon has elapsed

A jurisdiction that shows persistent C2 violations in the history usually indicates that interventions are being attempted but the authority lacks capability to complete them — a realistic outcome worth reporting.

---

## 9. Welfare

The welfare function is dimension-specific and prioritarian:

\[
W^* = W + \sum_d \gamma_d J^d - \sum_d \delta_d [J_{\min}^d - J^d]^+
\]

- The **first term** \( W \) is base flourishing, computed from base capabilities.
- The **second term** rewards justice directly.
- The **third term** penalizes justice deficits disproportionately.

### Reading welfare

```python
from gsm_governance import (
    welfare, welfare_dimension_specific, welfare_components,
)

# Scalar welfare (backward-compatible)
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

### Inspecting welfare components

```python
comps = welfare_components(sim.base_welfare(), gov, config)

print(f"Base welfare:         {comps['base']:.4f}")
print(f"Justice contribution: {comps['justice_contribution']:+.4f}")
print(f"Prioritarian penalty: {comps['prioritarian_penalty']:+.4f}")
print(f"Total W*:             {comps['W_star']:.4f}")
```

### Understanding the prioritarian commitment

The default parameters set \( \delta_d = 2.0 \, w_d \) and \( \gamma_d = 0.75 \, w_d \). This means:

- Improving justice from 0.5 to 0.6 raises welfare by \( 0.75 \cdot w_d \cdot 0.1 \).
- Bringing a jurisdiction from below floor to at floor raises welfare by \( 2.0 \cdot w_d \cdot (\text{deficit}) \).

The ratio \( \delta_d / \gamma_d = 2.67 \) encodes the view that **fixing deficits matters more than further improving the just**. This is a normative choice, not a derivation.

### Customizing the weights

```python
config.gamma_dim = {d: 0.5 for d in gsm.JUSTICE_DIMENSIONS}
config.delta_dim = {d: 1.5 for d in gsm.JUSTICE_DIMENSIONS}
config.validate()
```

Note that `delta_dim[d] > gamma_dim[d]` is enforced. To relax this, you must bypass validation (not recommended).

---

## 10. Interventions

When a constraint is violated, the enforcer schedules a **policy intervention**: a designated authority raises the affected state over a finite horizon, at a cost distributed across capabilities.

### What an intervention looks like

```python
# After running the simulation, inspect active interventions
for iv in sim.enforcer.active:
    print(f"Authority: {iv['authority']}")
    print(f"Jurisdiction: {iv['jurisdiction']}")
    print(f"Dimension: {iv['dimension']}")
    print(f"From {iv['from']:.3f} to {iv['to']:.3f}")
    print(f"Steps remaining: {iv['steps_remaining']}")
    print(f"Total cost: {iv['cost']:.4f}")
    print(f"Reason: {iv['reason']}")
    print()
```

### Aggregate intervention statistics

```python
print(sim.enforcer.stats)
# {'scheduled': 42, 'completed': 40, 'total_cost': 3.2814}

print(f"Active interventions: {sim.enforcer.active_count}")
```

### Multi-channel costs

Every intervention cost is distributed across four capabilities:

| Channel | Default weight | Rationale |
|---|---|---|
| `C` | 0.50 | Administrative capacity is the primary constraint |
| `S` | 0.25 | Interventions frequently produce short-term polarization |
| `T` | 0.15 | Overturning prior commitments weakens continuity |
| `A` | 0.10 | Override of local decision-making has modest accountability cost |

To reproduce v0.2.0-style single-channel behavior (cost charged only to competence):

```python
from gsm_governance import GSMConfig

config = GSMConfig(
    intervention_weights={"C": 1.0, "S": 0.0, "T": 0.0, "A": 0.0}
)
```

### Passive recovery

Once interventions conclude, capabilities recover gradually:

```python
config = GSMConfig(
    recovery={"C": 0.05, "S": 0.05, "T": 0.05, "A": 0.05}
)
```

Recovery is inactive while any intervention is in progress.

### The frequency ceiling

Because interventions consume capability, aggressive justice improvement is **self-limiting**. In the demonstration:

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState, Simulation,
)

def build(config):
    gov = MultiLevelGovernance(config=config)
    gov.add_jurisdiction("P", level=3)
    gov.add_jurisdiction(
        "C", level=2,
        justice=JusticeState({d: 0.05 for d in [
            "distributive", "procedural", "recognition",
            "corrective", "intergenerational",
        ]}),
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
          f"cumulative cost = {history[-1]['total_cost']:.4f}")
```

Under single-channel costs, cohesion and continuity are untouched, so aggressive intervention proceeds indefinitely. Under multi-channel costs, cohesion and continuity degrade, and the total number of completed interventions falls materially.

---

# Part III — Building models

## 11. Building a hierarchy from scratch

For real applications, you will not use the demonstration hierarchy. This section walks through constructing a custom multi-level model.

### Step 1 — Decide on levels and units

Suppose you are modelling a federal system:

- Level 4: national government
- Level 3: state governments
- Level 2: municipal governments
- Level 1: households (not modelled individually)

### Step 2 — Instantiate configuration

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeInteractionMatrix, MJRegime,
)

config = GSMConfig()
gov = MultiLevelGovernance(config=config)
M = JusticeInteractionMatrix(regime=MJRegime.SYMMETRIC)
```

### Step 3 — Add jurisdictions

```python
from gsm_governance import JusticeState

# National level
gov.add_jurisdiction(
    "national", level=4,
    capabilities={"A": 0.70, "C": 0.75, "S": 0.60, "T": 0.65, "L": 0.70},
    justice=JusticeState({
        "distributive": 0.55,
        "procedural": 0.60,
        "recognition": 0.35,
        "corrective": 0.25,
        "intergenerational": 0.45,
    }),
)

# State level
states = {
    "state_east": {"A": 0.75, "C": 0.80, "S": 0.70, "T": 0.65, "L": 0.70},
    "state_west": {"A": 0.60, "C": 0.65, "S": 0.55, "T": 0.60, "L": 0.55},
    "state_north": {"A": 0.70, "C": 0.60, "S": 0.65, "T": 0.55, "L": 0.60},
}
for uid, caps in states.items():
    gov.add_jurisdiction(uid, level=3, capabilities=caps)

# Municipalities
municipalities = {
    "city_alpha":   {"distributive": 0.70, "procedural": 0.65, "recognition": 0.50,
                     "corrective": 0.30, "intergenerational": 0.55},
    "city_beta":    {"distributive": 0.45, "procedural": 0.40, "recognition": 0.25,
                     "corrective": 0.15, "intergenerational": 0.30},
    "city_gamma":   {"distributive": 0.60, "procedural": 0.55, "recognition": 0.35,
                     "corrective": 0.20, "intergenerational": 0.45},
    "city_delta":   {"distributive": 0.55, "procedural": 0.50, "recognition": 0.20,
                     "corrective": 0.10, "intergenerational": 0.35},
}
for uid, j_vals in municipalities.items():
    gov.add_jurisdiction(uid, level=2, justice=JusticeState(j_vals))
```

### Step 4 — Link the hierarchy

```python
# Vertical
gov.link_vertical("national", "state_east")
gov.link_vertical("national", "state_west")
gov.link_vertical("national", "state_north")

gov.link_vertical("state_east", "city_alpha")
gov.link_vertical("state_east", "city_beta")
gov.link_vertical("state_west", "city_gamma")
gov.link_vertical("state_north", "city_delta")

# Horizontal (neighbour states)
gov.link_horizontal("state_east", "state_west")
gov.link_horizontal("state_west", "state_north")

# Horizontal (neighbour cities)
gov.link_horizontal("city_alpha", "city_beta")
```

### Step 5 — Run and inspect

```python
from gsm_governance import Simulation

sim = Simulation(gov, config=config, M_J=M)
history = sim.run(steps=500)

print(f"Final W*: {history[-1]['W_star']:.4f}")
print(f"Mean justice: {history[-1]['mean_justice']:.4f}")
```

---

## 12. Injecting exploitation and compensation

The exploitation matrix `E_ij` records, for each ordered pair `(i, j)`, how much jurisdiction `i` extracts from `j` uncompensated. Each entry is a dict across five justice dimensions.

### Setting up exploitation

```python
sim.set_exploitation("state_east", "city_beta", {
    "distributive": 0.25,
    "procedural": 0.15,
    "recognition": 0.20,
    "corrective": 0.00,
    "intergenerational": 0.10,
})
```

### Setting up compensation

```python
sim.set_compensation("state_east", "city_beta", {
    "distributive": 0.15,
    "procedural": 0.05,
    "recognition": 0.00,
    "corrective": 0.00,
    "intergenerational": 0.05,
})
```

### Using `CompensationVector` (six-component form)

```python
from gsm_governance import CompensationVector

cv = CompensationVector(
    fiscal=0.10,
    infrastructural=0.05,
    representational=0.02,
    regulatory=0.03,
    future_oriented=0.02,
    restitutional=0.00,
)
print(cv.total())              # 0.22
print(cv.to_justice_dimensions())
# {'distributive': 0.08,
#  'procedural': 0.025,
#  'recognition': 0.025,
#  'corrective': 0.02,
#  'intergenerational': 0.035}
```

To register a `CompensationVector` on a `CompensationMechanism`:

```python
from gsm_governance import CompensationMechanism

cm = CompensationMechanism()
cm.add_vector("state_east", "city_beta", cv)
```

### Reading exploitation

```python
em = sim.exploitation
total = em.total("state_east", "city_beta")
print(f"Total exploitation: {total:.3f}")

per_dim = em.get("state_east", "city_beta")
for d, v in per_dim.items():
    print(f"  {d:20s}: {v:.3f}")
```

### Why dimension-level decomposition matters

Non-exploitation in one dimension does not imply non-exploitation in another. A jurisdiction may pay fair prices (distributive = 0) while dominating decision-making (procedural > 0) and depleting commons (intergenerational > 0).

Decomposing exploitation by dimension ensures that:

1. The vulnerability-sensitive constraint (C3) can target *any* dimension.
2. Compensation can be matched to the specific harm.
3. The justice dynamics can erode the corresponding dimension.

---

## 13. Configuring normative parameters

The `GSMConfig` class holds both structural and normative parameters. Every study must specify and justify the normative ones.

### Justice weights

```python
config = GSMConfig()
config.justice_weights = {
    "distributive": 0.30,
    "procedural": 0.20,
    "recognition": 0.25,
    "corrective": 0.10,
    "intergenerational": 0.15,
}
config.validate()
```

Weights must sum to 1 and be non-negative.

### Justice floors

```python
config.justice_floors = {
    "distributive": 0.35,   # raised from default 0.30
    "procedural": 0.30,
    "recognition": 0.30,    # raised from default 0.25
    "corrective": 0.15,
    "intergenerational": 0.25,
}
```

Document your justification:

```python
print(config.justify_floor("distributive", "capability"))
# "distributive=0.350 justified by capability framework"
```

### Prioritarian coefficients

```python
# Default: gamma_d = 0.75 * w_d, delta_d = 2.0 * w_d
# Override for a stronger prioritarian stance
config.delta_dim = {d: 3.0 * config.justice_weights[d]
                    for d in config.justice_weights}
```

### Accountability penalties

```python
config.lambda_p_dim = {
    "distributive": 0.25,
    "procedural": 0.25,
    "recognition": 0.50,
    "corrective": 0.15,
    "intergenerational": 0.40,
}
```

### Subsidiarity

```python
config.phi = 0.90   # tighter vertical alignment (default 0.85)
config.phi = 1.00   # perfect non-regression
config.phi = 0.00   # C4 disabled
```

### C4 mode

```python
from gsm_governance import C4Mode

config.c4_mode = C4Mode.PER_DIMENSION   # default
config.c4_mode = C4Mode.AGGREGATE
config.c4_mode = C4Mode.HYBRID
```

### Validation

```python
try:
    config.validate()
    print("Parameters are valid")
except ValueError as e:
    print(f"Invalid: {e}")
```

---

## 14. Configuring structural parameters

Structural parameters describe dynamics and enforcement. They are empirical or modeling choices subject to calibration.

### Justice dynamics

```python
# Diffusion rate across neighbours (default 0.20)
config.eta = 0.30

# Decay per dimension (default 0.05)
config.kappa_d = {d: 0.03 for d in config.justice_weights}

# Internal coupling (support from base capabilities)
config.alpha_d = {
    "distributive":      0.35,
    "procedural":        0.35,
    "recognition":       0.30,
    "corrective":        0.25,
    "intergenerational": 0.40,
}

# Corrective restorative coupling
config.alpha_corrective_restorative = 0.40
```

### Exploitation dynamics

```python
config.beta_erosion = {d: 0.50 for d in config.justice_weights}
config.beta_compensation = {d: 0.60 for d in config.justice_weights}
config.mu = 0.30   # justice suppression of exploitation (default 0.25)
```

### Accountability coupling

```python
config.lam_c = 0.20   # parent-child accountability convergence (default 0.15)
```

### Intervention costs

```python
config.intervention_cost = 0.15
config.intervention_horizon = 10
config.intervention_weights = {"C": 0.40, "S": 0.30, "T": 0.20, "A": 0.10}
config.recovery = {"C": 0.08, "S": 0.06, "T": 0.06, "A": 0.05}
```

### Validation

```python
config.validate()   # ensures intervention weights sum to 1
```

---

# Part IV — Running experiments

## 15. Running and inspecting simulations

### Basic run

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState, Simulation,
)

config = GSMConfig()
gov = MultiLevelGovernance(config=config)
gov.add_jurisdiction("X", level=4)

sim = Simulation(gov, config=config)
history = sim.run(steps=500)
```

`history` is a list of dicts, one per step:

```python
last = history[-1]
print(last)
# {
#   't': 25.0,
#   'W_star': 3.4821,
#   'mean_justice': 0.5104,
#   'dim_means': {'distributive': 0.62, ...},
#   'C1_violations': 0,
#   'C2_violations': 0,
#   'C3_violations': 0,
#   'C4_violations': 0,
#   'active_interventions': 0,
#   'total_cost': 2.7413,
# }
```

### Extracting time series

```python
import pandas as pd

df = pd.DataFrame(history)

# Welfare trajectory
print(df[["t", "W_star"]].tail())

# Dimension-specific justice trajectory
dim_df = pd.DataFrame([r["dim_means"] for r in history])
dim_df["t"] = df["t"]
print(dim_df.tail())
```

### Plotting

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

axes[0].plot(df["t"], df["W_star"])
axes[0].set_ylabel("W*")
axes[0].set_title("Welfare trajectory")

axes[1].plot(df["t"], df["mean_justice"])
axes[1].set_ylabel("Mean justice")
axes[1].set_xlabel("Time")

plt.tight_layout()
plt.savefig("welfare_trajectory.png", dpi=150)
```

### Per-dimension trajectory

```python
for d in config.justice_weights:
    plt.gca().plot(dim_df["t"], dim_df[d], label=d)

plt.legend()
plt.xlabel("Time")
plt.ylabel("Justice dimension")
plt.savefig("dimension_trajectories.png", dpi=150)
```

### Inspecting interventions over time

```python
df["active_interventions"].plot()
plt.xlabel("Time")
plt.ylabel("Active interventions")
plt.savefig("interventions_over_time.png", dpi=150)
```

---

## 16. Scenario comparisons

The library exposes scenario construction through explicit configuration variation.

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState, Simulation,
)

def build_gov(config, communities_justice=None):
    gov = MultiLevelGovernance(config=config)
    gov.add_jurisdiction("G", level=4)
    gov.add_jurisdiction("R", level=3)
    gov.add_jurisdiction(
        "C", level=2,
        justice=JusticeState(communities_justice or {
            "distributive": 0.20, "procedural": 0.20,
            "recognition": 0.20, "corrective": 0.20,
            "intergenerational": 0.20,
        }),
    )
    gov.link_vertical("G", "R")
    gov.link_vertical("R", "C")
    return gov

scenarios = {}

# Default
cfg = GSMConfig()
scenarios["default"] = Simulation(build_gov(cfg), config=cfg)

# No floor
cfg = GSMConfig()
cfg.justice_floors = {d: 0.0 for d in cfg.justice_weights}
scenarios["no_floor"] = Simulation(build_gov(cfg), config=cfg)

# No subsidiarity
cfg = GSMConfig(phi=0.0)
scenarios["no_subsidiarity"] = Simulation(build_gov(cfg), config=cfg)

# Single-channel intervention cost
cfg = GSMConfig(intervention_weights={"C": 1.0, "S": 0.0, "T": 0.0, "A": 0.0})
scenarios["single_channel"] = Simulation(build_gov(cfg), config=cfg)

# Run all
results = {}
for name, sim in scenarios.items():
    results[name] = sim.run(steps=500)

# Compare welfare trajectories
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 6))
for name, hist in results.items():
    df = pd.DataFrame(hist)
    ax.plot(df["t"], df["W_star"], label=name)

ax.set_xlabel("Time")
ax.set_ylabel("W*")
ax.set_title("Scenario comparison")
ax.legend()
plt.savefig("scenario_comparison.png", dpi=150)
```

### Interpreting differences

- **`no_floor` vs. `default`**: isolates the effect of constraint C2 on welfare and dimension-specific justice.
- **`no_subsidiarity` vs. `default`**: isolates the effect of vertical alignment.
- **`single_channel` vs. `default`**: tests the frequency ceiling prediction.

---

## 17. Sensitivity analysis

### Sweeping a single parameter

```python
import numpy as np
import matplotlib.pyplot as plt
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, Simulation,
)

phis = np.linspace(0.0, 1.0, 11)
final_welfare = []

for phi in phis:
    config = GSMConfig(phi=phi)
    gov = MultiLevelGovernance(config=config)
    gov.add_jurisdiction("G", level=4)
    gov.add_jurisdiction("C", level=2)
    gov.link_vertical("G", "C")
    sim = Simulation(gov, config=config)
    hist = sim.run(steps=300)
    final_welfare.append(hist[-1]["W_star"])

plt.plot(phis, final_welfare, marker="o")
plt.xlabel("phi (subsidiarity tolerance)")
plt.ylabel("Final W*")
plt.savefig("sensitivity_phi.png", dpi=150)
```

### Sweeping multiple parameters

```python
from itertools import product
import pandas as pd

lambda_p_base = [0.20, 0.30, 0.40]
delta_ratio = [1.5, 2.0, 3.0]

results = {}
for lpb, dr in product(lambda_p_base, delta_ratio):
    config = GSMConfig()
    config.lambda_p_dim = {d: lpb for d in config.justice_weights}
    config.gamma_dim = {d: 0.5 * config.justice_weights[d]
                        for d in config.justice_weights}
    config.delta_dim = {d: dr * config.gamma_dim[d]
                        for d in config.gamma_dim}
    config.validate()

    gov = MultiLevelGovernance(config=config)
    gov.add_jurisdiction("G", level=4)
    gov.add_jurisdiction("C", level=2)
    gov.link_vertical("G", "C")

    sim = Simulation(gov, config=config)
    hist = sim.run(steps=300)
    results[(lpb, dr)] = hist[-1]["W_star"]

df = pd.DataFrame(
    [[results[(lpb, dr)] for dr in delta_ratio] for lpb in lambda_p_base],
    index=[f"lambda_p={x}" for x in lambda_p_base],
    columns=[f"delta/gamma={x}" for x in delta_ratio],
)
print(df)
```

### Weight sweep over the justice simplex

```python
import numpy as np

def simplex_sample(n_samples=20):
    samples = []
    for _ in range(n_samples):
        cuts = sorted(np.random.uniform(0, 1, 4))
        w = np.diff([0] + cuts + [1])
        samples.append(w)
    return samples

for w in simplex_sample(20):
    config = GSMConfig()
    config.justice_weights = dict(zip(config.justice_weights.keys(), w))
    try:
        config.validate()
    except ValueError:
        continue
    gov = MultiLevelGovernance(config=config)
    gov.add_jurisdiction("X", level=4)
    sim = Simulation(gov, config=config)
    hist = sim.run(steps=200)
    print(f"Weights {w.round(2)} -> W* = {hist[-1]['W_star']:.4f}")
```

---

## 18. Visualization

The library provides optional visualization helpers.

```python
from gsm_governance.utils.visualization import (
    plot_welfare,
    plot_dimension_trajectories,
    plot_interventions,
    plot_justice_radar,
)

plot_welfare(history, save_path="welfare.png")
plot_dimension_trajectories(history, save_path="dimensions.png")
plot_interventions(history, save_path="interventions.png")
plot_justice_radar(gov, uids=["national", "region", "community"],
                   save_path="radar.png")
```

If `matplotlib` is not installed, these functions raise an informative `ImportError` suggesting:

```bash
pip install gsm-governance[viz]
```

### Custom plots

For custom plots, use `history` directly:

```python
import matplotlib.pyplot as plt
import numpy as np

times = [r["t"] for r in history]
fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

axes[0].plot(times, [r["W_star"] for r in history])
axes[0].set_ylabel("W*")

axes[1].plot(times, [r["mean_justice"] for r in history])
axes[1].set_ylabel("Mean justice")

axes[2].plot(times, [r["active_interventions"] for r in history])
axes[2].set_ylabel("Active interventions")
axes[2].set_xlabel("Time")

plt.tight_layout()
plt.savefig("overview.png", dpi=150)
```

---

# Part V — Advanced usage

## 19. Custom dynamics

You can subclass `Simulation` to substitute alternative dynamics.

### Example: add an exogenous shock at time t=10

```python
from gsm_governance import Simulation

class ShockSimulation(Simulation):
    def __init__(self, *args, shock_time=10.0, shock_magnitude=0.3, **kwargs):
        super().__init__(*args, **kwargs)
        self.shock_time = shock_time
        self.shock_magnitude = shock_magnitude
        self._applied = False

    def step(self):
        super().step()
        if not self._applied and self.t >= self.shock_time:
            for j in self.governance.jurisdictions.values():
                cur = j.state.justice.d["distributive"]
                j.state.justice.d["distributive"] = max(
                    0.0, cur - self.shock_magnitude)
            self._applied = True
```

### Example: remove the justice suppression of exploitation

```python
class NoSuppressionSimulation(Simulation):
    def step(self):
        self.config.mu = 0.0
        super().step()
```

### Example: capture per-step diagnostics

```python
import numpy as np

class DiagnosticSimulation(Simulation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.diagnostics = []

    def step(self):
        super().step()
        self.diagnostics.append({
            "t": self.t,
            "active": self.enforcer.active_count,
            "scheduled": self.enforcer.stats["scheduled"],
            "mean_A": float(np.mean([
                j.state.A for j in self.governance.jurisdictions.values()
            ])),
        })
```

### Example: custom justice step

If you need to replace the standard justice dynamics entirely:

```python
from gsm_governance import Simulation

class CustomJusticeSimulation(Simulation):
    def step(self):
        # Custom pre-step: manual justice adjustment
        for j in self.governance.jurisdictions.values():
            j.state.justice.d["distributive"] += 0.001

        # Then run the standard step
        super().step()
```

---

## 20. Custom enforcement

You can subclass `PolicyInterventionEnforcer` for alternative cost or scheduling rules.

### Example: quadratic cost

```python
from gsm_governance import (
    PolicyInterventionEnforcer, INTERVENTION_CHANNELS,
)

class QuadraticCostEnforcer(PolicyInterventionEnforcer):
    def _charge_capability_cost(self, auth, cost_per_step):
        scaled = cost_per_step ** 1.5
        for k in INTERVENTION_CHANNELS:
            w = self.config.intervention_weights.get(k, 0.0)
            cur = getattr(auth.state, k)
            new = max(0.0, cur - w * scaled)
            setattr(auth.state, k, new)
```

### Example: bounded intervention rate

```python
class RateLimitedEnforcer(PolicyInterventionEnforcer):
    def __init__(self, *args, max_per_step=3, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_per_step = max_per_step

    def check_and_schedule(self, governance, exploitation):
        super().check_and_schedule(governance, exploitation)
        # Truncate active list to the rate limit
        if len(self._active) > self.max_per_step:
            dropped = self._active[self.max_per_step:]
            self._active = self._active[:self.max_per_step]
            for iv in dropped:
                self._stats["scheduled"] -= 1
```

### Using a custom enforcer

```python
from gsm_governance import Simulation, GSMConfig

config = GSMConfig()
gov = ...
enforcer = RateLimitedEnforcer(config, max_per_step=2)
sim = Simulation(gov, config=config, enforcer=enforcer)
```

---

## 21. Empirical calibration of M_J

The library ships with theoretical priors. Fitting `M_J` to data follows the protocol in Appendix D of the manuscript.

### Structure of the estimation problem

Given observed justice indicators over time for many jurisdictions, you estimate:

- The **latent justice states** (unobserved)
- The **interaction matrix** `M_J`
- The **internal coupling coefficients** `alpha_d`

### Minimal interface

```python
from gsm_governance import JusticeInteractionMatrix, MJRegime

# Example: fitted coefficients from external estimation
fitted = {
    ("procedural", "recognition"):        +0.18,
    ("recognition", "procedural"):        +0.16,
    ("distributive", "corrective"):       +0.13,
    ("corrective", "recognition"):        +0.22,
    ("intergenerational", "distributive"): -0.07,
    # ...
}

M = JusticeInteractionMatrix(regime=MJRegime.ASYMMETRIC)
M.m = fitted
M.m_max = 0.30
```

### Data loader

The library provides a placeholder loader:

```python
from gsm_governance.data import load_justice_indicators

# Returns {} unless a path to a local CSV is supplied
indicators = load_justice_indicators("path/to/indicators.csv")
```

The expected CSV format is a long-form panel with columns `uid`, `t`, and one column per justice dimension.

### Reporting

When using fitted matrices, report:

- The number of observations and jurisdictions
- The sign priors used
- The estimation regime (symmetric or asymmetric)
- Posterior means and 90% credible intervals
- Sensitivity to `m_max`

### Simulated workflow

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, Simulation,
    JusticeInteractionMatrix, MJRegime,
)

# 1. Load observed indicator panel (external)
# indicators = pd.read_csv("justice_indicators.csv")

# 2. Fit hierarchical Bayesian model (external; not implemented in this library)
# posterior = fit_hierarchical_model(indicators, sign_priors={...})

# 3. Construct the interaction matrix
M = JusticeInteractionMatrix(regime=MJRegime.ASYMMETRIC)
# M.m = posterior["m_de_mean"]

# 4. Run forward simulations with the fitted matrix
config = GSMConfig()
gov = ...
sim = Simulation(gov, config=config, M_J=M)
hist = sim.run(steps=500)
```

---

## 22. Extending the justice dimensions

The model is designed around five dimensions, but you may wish to add others (e.g., ecological, territorial, epistemic).

### Step 1 — Extend the dimension constants

Because the library iterates over `JUSTICE_DIMENSIONS` in most places, the cleanest approach is to patch the tuple and the corresponding dictionaries in a small extension module:

```python
import gsm_governance as gsm

# Extend the module-level tuple
gsm.JUSTICE_DIMENSIONS = (
    "distributive", "procedural", "recognition",
    "corrective", "intergenerational", "ecological",
)
```

### Step 2 — Update configuration

```python
config = gsm.GSMConfig()
config.justice_weights["ecological"] = 0.10
# Renormalize
total = sum(config.justice_weights.values())
config.justice_weights = {k: v / total
                          for k, v in config.justice_weights.items()}

config.justice_floors["ecological"] = 0.20
config.gamma_dim["ecological"] = 0.75 * config.justice_weights["ecological"]
config.delta_dim["ecological"] = 2.0 * config.justice_weights["ecological"]
config.lambda_p_dim["ecological"] = 0.35

config.alpha_d["ecological"] = 0.30
config.kappa_d["ecological"] = 0.05
config.beta_erosion["ecological"] = 0.40
config.beta_compensation["ecological"] = 0.50
```

### Step 3 — Update the interaction matrix

```python
M = gsm.JusticeInteractionMatrix()
M.m[("ecological", "intergenerational")] = +0.20
M.m[("intergenerational", "ecological")] = +0.20
M.m[("ecological", "distributive")] = -0.10
```

### Step 4 — Run

```python
gov = gsm.MultiLevelGovernance(config=config)
gov.add_jurisdiction(
    "X", level=4,
    justice=gsm.JusticeState({
        "distributive": 0.65, "procedural": 0.55,
        "recognition": 0.30, "corrective": 0.20,
        "intergenerational": 0.45, "ecological": 0.40,
    }),
)
sim = gsm.Simulation(gov, config=config, M_J=M)
history = sim.run(steps=300)
```

**Caveat.** The five-dimensional architecture is not arbitrary. Each dimension corresponds to a distinct tradition in justice theory (Rawlsian distribution, deliberative procedure, recognition theory, historical injustice, intergenerational ethics). Adding dimensions risks conceptual overlap and reviewer skepticism. If you extend, document the theoretical justification carefully.

---

# Part VI — Reference

## 23. Common patterns and recipes

### Recipe 1 — Measure the effect of a single constraint

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, Simulation,
)

def run_with(config):
    gov = MultiLevelGovernance(config=config)
    gov.add_jurisdiction("G", level=4)
    gov.add_jurisdiction("C", level=2)
    gov.link_vertical("G", "C")
    sim = Simulation(gov, config=config)
    return sim.run(steps=500)

# With floor
config_with = GSMConfig()
hist_with = run_with(config_with)

# Without floor
config_without = GSMConfig()
config_without.justice_floors = {d: 0.0 for d in config_without.justice_weights}
hist_without = run_with(config_without)

print(f"With floor:    W* = {hist_with[-1]['W_star']:.4f}")
print(f"Without floor: W* = {hist_without[-1]['W_star']:.4f}")
```

### Recipe 2 — Identify jurisdictions below floor

```python
for uid, j in gov.jurisdictions.items():
    deficits = j.state.justice.floor_deficits(config.justice_floors)
    for d, def_val in deficits.items():
        if def_val > 0:
            print(f"{uid} below {d} floor by {def_val:.3f}")
```

### Recipe 3 — Trace a justice dimension through time

```python
import matplotlib.pyplot as plt

history = sim.run(steps=500)
distributive_series = [r["dim_means"]["distributive"] for r in history]

plt.plot(distributive_series)
plt.xlabel("Step")
plt.ylabel("Mean distributive justice")
plt.title("Distributive justice trajectory")
plt.savefig("distributive_trajectory.png", dpi=150)
```

### Recipe 4 — Test a specific intervention policy

```python
from gsm_governance import Simulation

class EarlyInterventionSimulation(Simulation):
    def step(self):
        # Aggressive early intervention
        if self.t < 5.0:
            self.config.intervention_horizon = 2
        else:
            self.config.intervention_horizon = 10
        super().step()
```

### Recipe 5 — Export a jurisdiction's state to JSON

```python
import json

def jurisdiction_to_dict(j):
    return {
        "uid": j.uid,
        "level": j.level,
        "capabilities": j.state.capabilities(),
        "justice": j.state.justice.as_dict(),
        "parent": j.parent,
        "children": j.children,
        "neighbours": j.neighbours,
    }

with open("jurisdictions.json", "w") as f:
    json.dump(
        {uid: jurisdiction_to_dict(j)
         for uid, j in gov.jurisdictions.items()},
        f, indent=2,
    )
```

### Recipe 6 — Batch run over many parameter configurations

```python
from itertools import product
import pandas as pd
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, Simulation,
)

configs = list(product(
    [0.60, 0.85, 1.00],                # phi
    [0.20, 0.30, 0.40],                # lambda_p base
    ["symmetric", "asymmetric"],
))

rows = []
for phi, lpb, regime in configs:
    config = GSMConfig(phi=phi)
    config.lambda_p_dim = {d: lpb for d in config.justice_weights}

    M = JusticeInteractionMatrix(regime=MJRegime(regime))

    gov = MultiLevelGovernance(config=config)
    gov.add_jurisdiction("G", level=4)
    gov.add_jurisdiction("C", level=2)
    gov.link_vertical("G", "C")

    sim = Simulation(gov, config=config, M_J=M)
    hist = sim.run(steps=300)

    rows.append({
        "phi": phi,
        "lambda_p": lpb,
        "regime": regime,
        "W_star": hist[-1]["W_star"],
        "C2_violations": hist[-1]["C2_violations"],
    })

df = pd.DataFrame(rows)
df.to_csv("batch_results.csv", index=False)
print(df)
```

---

## 24. Troubleshooting

### "Invalid: justice weights must sum to 1"

Your `justice_weights` do not sum to 1. Renormalize:

```python
total = sum(config.justice_weights.values())
config.justice_weights = {k: v / total
                          for k, v in config.justice_weights.items()}
config.validate()
```

### "Invalid: prioritarian penalty must exceed welfare weight"

You have `delta_dim[d] <= gamma_dim[d]` for some dimension. Set `delta_dim[d] > gamma_dim[d]`, e.g., `delta_dim[d] = 2 * gamma_dim[d]`.

### "Invalid: intervention weights must sum to 1"

Adjust `intervention_weights` so the four entries sum to 1.

### Simulation produces NaN or Inf

Usually a sign of an unstable parameter combination. Check:

- `config.dt` is small enough (try 0.01)
- Coupling coefficients are within `[-m_max, m_max]`
- Diffusion rate `eta` is below 1

### All jurisdictions below floor with no improvement

Check that:

- `intervention_horizon` is positive
- The designated authority has capability to intervene
- `intervention_cost` is not so high that scheduling is infeasible

### Frequency ceiling appears too early

Reduce `intervention_cost`, increase `recovery` rates, or reduce the number of dimensions requiring intervention.

### Violations persist despite active interventions

Check `steps_remaining` on active interventions. If the horizon exceeds the simulation length, violations will persist by design.

### "KeyError: unknown justice dimension"

You tried to access a dimension key that is not in `JUSTICE_DIMENSIONS`. Verify the spelling — dimensions are lowercase and use full words:

```python
"distributive"      # correct
"Distributive"      # wrong
"dist"              # wrong
```

### `hfi(gov)` returns a value different from v0.2.0

`hfi` in 0.3.0 combines base capabilities with aggregate justice; v0.2.0 used only base capabilities. To reproduce the v0.2.0 value:

```python
import numpy as np
from gsm_governance import BASE_CAPABILITIES

v02_hfi = float(np.mean([
    np.mean([getattr(j.state, k) for k in BASE_CAPABILITIES])
    for j in gov.jurisdictions.values()
]))
```

---

## 25. Glossary

| Term | Definition |
|---|---|
| **Bounded non-exploitation** | Normative constraint: no jurisdiction may impose uncompensated non-trivial sacrifices on another |
| **Capability** | One of six governance subsystems: accountability, competence, cohesion, continuity, learning, justice |
| **C1, C2, C3, C4** | The four justice constraints (bounded non-exploitation, floor, vulnerability-sensitive, vertical alignment) |
| **Dimension** | One of five justice components: distributive, procedural, recognition, corrective, intergenerational |
| **Enforcement mode** | How constraints are enforced: projection, penalty, or hybrid |
| **Exploitation index** | `E_ij`, the amount jurisdiction `i` extracts from `j` |
| **Floor** | Minimum acceptable value of a justice dimension |
| **Frequency ceiling** | Endogenous limit on intervention rate from multi-channel cost |
| **Interaction matrix** | `M_J`, signed matrix of synergies and tensions between justice dimensions |
| **Intervention** | A policy action that raises a state over a finite horizon at a capability cost |
| **Level** | An integer index in the governance hierarchy |
| **Prioritarian** | Weighting improvements to the worst off more heavily |
| **Subsidiarity** | Higher levels may not erode justice achieved at lower levels |
| **Superset** | GSM-J 0.3.0 preserves all v0.2.0 APIs while adding new functionality |
| **Vertical alignment** | Constraint C4, enforcing subsidiarity |

---

**End of user guide.**

For the mathematical specification, see the manuscript. For the API reference, see the docstrings in each module. For worked examples, see the `examples/` directory in the repository.

If you find errors or have suggestions, please open an issue on GitHub.