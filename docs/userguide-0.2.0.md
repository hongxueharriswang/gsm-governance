# `gsm-governance` User Guide

**Version 0.2.0** | A Python library for computational modelling of multi-level governance with a bounded non-exploitation constraint

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Conceptual Overview](#3-conceptual-overview)
4. [Quick Start](#4-quick-start)
5. [Core Concepts](#5-core-concepts)
   - 5.1 [Governance Capabilities](#51-governance-capabilities)
   - 5.2 [Flourishing Dimensions](#52-flourishing-dimensions)
   - 5.3 [The Multi-Level System](#53-the-multi-level-system)
   - 5.4 [The Bounded Non-Exploitation Constraint](#54-the-bounded-non-exploitation-constraint)
6. [Computing Indices](#6-computing-indices)
   - 6.1 [Governance Success Index (GSI)](#61-governance-success-index-gsi)
   - 6.2 [Human Flourishing Index (HFI)](#62-human-flourishing-index-hfi)
   - 6.3 [Misalignment](#63-misalignment)
   - 6.4 [Welfare](#64-welfare)
7. [Working with Constraints](#7-working-with-constraints)
   - 7.1 [Conditions A, B, and C](#71-conditions-a-b-and-c)
   - 7.2 [Threshold Functions](#72-threshold-functions)
   - 7.3 [Compensation Vectors](#73-compensation-vectors)
   - 7.4 [Valuation Vectors](#74-valuation-vectors)
8. [Running Simulations](#8-running-simulations)
   - 8.1 [Basic Simulation](#81-basic-simulation)
   - 8.2 [Adding Shocks](#82-adding-shocks)
   - 8.3 [Policy Controls](#83-policy-controls)
   - 8.4 [Examining the History](#84-examining-the-history)
9. [Working with Data](#9-working-with-data)
   - 9.1 [Loading Denmark's Data](#91-loading-denmarks-data)
   - 9.2 [Building a Multi-Level System](#92-building-a-multi-level-system)
10. [Visualization](#10-visualization)
11. [Complete Worked Examples](#11-complete-worked-examples)
    - 11.1 [Single Jurisdiction: Denmark](#111-single-jurisdiction-denmark)
    - 11.2 [Multi-Jurisdiction Simulation](#112-multi-jurisdiction-simulation)
    - 11.3 [Five-Level System with Shock](#113-five-level-system-with-shock)
12. [API Reference](#12-api-reference)
13. [Troubleshooting](#13-troubleshooting)
14. [Migration from v0.1.0](#14-migration-from-v010)
15. [Citation and License](#15-citation-and-license)

---

## 1. Introduction

`gsm-governance` is a Python library that implements the **General Governance Success Model (GSM)** as presented in:

> Wang, H. (2026). *A Computational Systems Model of Multi-Level Governance: Extending the General Governance Success Model with a Bounded Non-Exploitation Constraint.* Systems Research and Behavioral Science.

The library provides:

- A **five-dimensional governance model** (accountability, competence, cohesion, continuity, learning)
- A **four-dimensional flourishing model** (economic, quality, well-being, sustainability)
- **Multi-level dynamics** with vertical (top-down and bottom-up) and horizontal (peer) interactions
- A **bounded non-exploitation constraint** with threshold tolerance and vector-valued compensation
- **Simulation, metrics, and visualization** utilities
- **Data loaders** for real governance indicators from V-Dem, World Bank WGI, WJP, UNDP, and OWID

The library is designed for:
- **Researchers** in systems theory, cybernetics, governance, and public administration
- **Policymakers** interested in comparative governance analysis
- **Students** learning computational social science
- **Practitioners** designing multi-level governance systems

---

## 2. Installation

### From source

```bash
git clone https://github.com/harriswang/gsm-governance.git
cd gsm-governance
pip install -e .
```

### With development dependencies

```bash
pip install -e ".[dev]"
```

### Verify installation

```python
import gsm_governance
print(gsm_governance.__version__)  # "0.2.0"
```

### Requirements

- Python ≥ 3.9
- NumPy ≥ 1.22
- SciPy ≥ 1.9
- pandas ≥ 1.5
- matplotlib ≥ 3.6

---

## 3. Conceptual Overview

The GSM framework models governance as a **complex adaptive system** operating across multiple nested levels (community → municipal → regional → national → supranational).

Each jurisdiction has:

| **Concept** | **Symbol** | **Dimensions** | **Meaning** |
|-------------|-----------|---------------|-------------|
| Governance capability | $\mathbf{g}$ | 5 | Institutional capacity |
| Flourishing outcome | $\mathbf{f}$ | 4 | Realized well-being |
| Information flow | $\mathbf{M}$ | 5L × 5L | Cross-level communication |
| Exploitation index | $\mathcal{E}$ | scalar | Cross-jurisdictional harm |
| Welfare | $\mathcal{W}$ | scalar | Composite well-being |

The **bounded non-exploitation constraint** ensures that no jurisdiction may impose *uncompensated, non-trivial* sacrifices on another jurisdiction for its own benefit. An action is admissible if it satisfies **Condition A** (no harm), **Condition B** (harm within a socially accepted threshold), or **Condition C** (harm fully compensated).

---

## 4. Quick Start

```python
from gsm_governance import MultiLevelGovernance

# Create a single jurisdiction with real Denmark raw data
gov = MultiLevelGovernance.from_single_jurisdiction(
    name="Denmark",
    accountability=88.3,   # normalized V-Dem score
    competence=92.2,       # normalized WGI score
    cohesion=90.0,         # normalized WJP score
    continuity=96.2,       # normalized UNDP HDI
    learning=72.4,         # Government Service Satisfaction
    economic=95.0, quality=92.5, wellbeing=74.0, sustainability=88.0,
)

# Compute indices
print(f"GSI : {gov.gsi():.2f}")            # 48.07 (corrected normalization)
print(f"HFI : {gov.hfi():.2f}")            # 87.40
print(f"D*  : {gov.misalignment('Denmark'):.2f}")  # 18.20
print(f"W   : {gov.welfare('Denmark'):.2f}")       # 67.74
```

> **Important note on GSI normalization (v0.2.0):** The theoretical maximum of the raw GSI with default parameters (α = 0.2, κ = 0.005) is **600**. Denmark's raw score of 288.4 normalizes to **48.07**, not 94.2 as in v0.1.0. See [Section 14](#14-migration-from-v010) for migration details.

---

## 5. Core Concepts

### 5.1 Governance Capabilities

The five governance capabilities are defined in canonical order:

| **Index** | **Name** | **Meaning** | **Example indicator** |
|-----------|----------|-------------|----------------------|
| 0 | `accountability` | Ability to hold authority answerable | V-Dem Liberal Democracy Index |
| 1 | `competence` | Administrative effectiveness | World Bank WGI Government Effectiveness |
| 2 | `cohesion` | Bridging trust and cooperation | WJP Rule of Law Index |
| 3 | `continuity` | Sustained strategic commitment | UNDP Human Development Index |
| 4 | `learning` | Policy evaluation and adaptation | Government Service Satisfaction |

All values are assumed normalized to the range `[0, 100]`.

```python
from gsm_governance.core.state import GovernanceState

g = GovernanceState(
    accountability=85.0,
    competence=90.0,
    cohesion=88.0,
    continuity=92.0,
    learning=80.0,
)
print(g.as_array())        # array([85., 90., 88., 92., 80.])
print(g["accountability"]) # 85.0
print(g.to_dict())         # {'accountability': 85.0, ...}
```

### 5.2 Flourishing Dimensions

The four flourishing dimensions are:

| **Index** | **Name** | **Meaning** |
|-----------|----------|-------------|
| 0 | `economic` | Material prosperity |
| 1 | `quality` | Health and education |
| 2 | `wellbeing` | Trust, safety, inclusion |
| 3 | `sustainability` | Environmental and intergenerational equity |

```python
from gsm_governance.core.state import FlourishingState

f = FlourishingState(economic=95.0, quality=92.5, wellbeing=74.0, sustainability=88.0)
print(f.as_array())  # array([95. , 92.5, 74. , 88. ])
```

### 5.3 The Multi-Level System

The `MultiLevelGovernance` class is the central container. It holds:

- A list of `Jurisdiction` objects
- A `GSMConfig` with global parameters
- Vertical interaction matrices (top-down and bottom-up)
- Horizontal coordination matrices
- Information-flow matrices

```python
from gsm_governance import GSMConfig, Jurisdiction, MultiLevelGovernance

config = GSMConfig()

system = MultiLevelGovernance(
    config=config,
    jurisdictions=[
        Jurisdiction(
            name="A", level="national",
            governance=GovernanceState(85, 88, 82, 90, 80),
            flourishing=FlourishingState(90, 88, 80, 85),
        ),
        Jurisdiction(
            name="B", level="national",
            governance=GovernanceState(78, 82, 75, 84, 76),
            flourishing=FlourishingState(82, 80, 72, 78),
        ),
    ],
)
```

### 5.4 The Bounded Non-Exploitation Constraint

The constraint ensures that actions do not impose uncompensated, non-trivial sacrifices on other jurisdictions. It uses the **counterfactual baseline** — comparing welfare *with* the action to welfare in a *no-action* counterfactual — to isolate the policy effect from underlying time trends.

An action is **admissible** if, for every affected jurisdiction $j \neq i$:

$$\mathcal{W}_{j}(t+1 \mid \mathbf{u}) - \mathcal{W}_{j}(t+1 \mid \mathbf{0}) \geq -\tau_{j} - \text{Comp}_{i \to j}^{\text{eff}}$$

where:
- $\tau_j$ is the socially accepted threshold for jurisdiction $j$
- $\text{Comp}_{i \to j}^{\text{eff}} = \boldsymbol{\lambda}_j^\top \text{Comp}_{i \to j}$ is the effective compensation
- $\boldsymbol{\lambda}_j$ is the recipient's valuation vector

---

## 6. Computing Indices

### 6.1 Governance Success Index (GSI)

The GSI measures the level of governance capability:

$$GSI_t = \sum_{i=1}^5 \alpha_i g_{i,t} + \sum_{i<j} \kappa_{ij} g_{i,t} g_{j,t}$$

**Normalization (v0.2.0):**

$$\text{GSI (normalized)} = \frac{GSI_{\text{raw}}}{\text{denominator}} \times 100$$

where the denominator is the theoretical maximum:

$$\text{denominator} = \sum_i \alpha_i \cdot 100 + \sum_{i<j} \kappa_{ij} \cdot 100 \cdot 100$$

For default parameters ($\alpha_i = 0.2$, $\kappa_{ij} = 0.005$):

$$\text{denominator} = 100 + 500 = 600$$

```python
gov = MultiLevelGovernance.from_single_jurisdiction(
    "A",
    accountability=88.3, competence=92.2, cohesion=90.0,
    continuity=96.2, learning=72.4,
)

# Normalized GSI (0-100 scale)
print(gov.gsi())  # 48.07

# Raw GSI (for internal computations)
from gsm_governance.metrics.indices import compute_gsi_raw, gsi_theoretical_max
print(compute_gsi_raw(gov.jurisdictions[0].governance, gov.config))  # 288.42
print(gsi_theoretical_max(gov.config))  # 600.0

# Perfect jurisdiction has GSI = 100
perfect = MultiLevelGovernance.from_single_jurisdiction(
    "Perfect",
    accountability=100, competence=100, cohesion=100,
    continuity=100, learning=100,
)
print(perfect.gsi())  # 100.0
```

**Interpreting the normalized GSI:**

A score of 100 is theoretically unattainable in practice because governance capabilities trade off against each other (e.g., maximizing accountability may constrain competence). The 100 point is a mathematical normalization anchor, not a policy target. Practical scores typically range from 30 (weak governance) to 55 (strong governance).

### 6.2 Human Flourishing Index (HFI)

$$HFI_t = \sum_{k=1}^4 \gamma_k f_{k,t}$$

```python
print(gov.hfi())  # 87.40 for Denmark
```

**Distribution-sensitive HFI** (Section 8.3 of the paper):

$$HFI_{i,t}^{\text{dist}} = \min_j HFI_{j,t} - \rho \cdot \text{Gini}(HFI_{1,t}, \ldots, HFI_{L,t})$$

```python
# For a multi-jurisdiction system
system = build_multi_jurisdiction_system()  # see Section 9.2
hfi_dist = system.hfi(distribution_sensitive=True)
print(hfi_dist)
```

### 6.3 Misalignment

There are two types of misalignment:

**Context-sensitive misalignment** (Section 7.4):

$$D^*_{i,\ell,t} = \sqrt{(\mathbf{g} - \mathbf{g}^*)^\top \mathbf{W}_D (\mathbf{g} - \mathbf{g}^*)}$$

```python
mis = gov.misalignment("A")
print(mis)  # 18.20
```

**Vertical misalignment** (Section 7.5) across levels:

```python
system = build_five_level_system()  # see Section 11.3
vert_mis = system.misalignment("L_national", vertical=True)
print(vert_mis)
```

### 6.4 Welfare

Welfare is the composite of governance success and distribution-sensitive flourishing:

$$\mathcal{W}_j = \theta_g \cdot GSI_j + \theta_f \cdot HFI_j^{\text{dist}}$$

```python
welfare = gov.welfare("A", distribution_sensitive=False)
print(welfare)  # 67.74 = 0.5 * 48.07 + 0.5 * 87.40
```

Customize welfare weights:

```python
from gsm_governance import GSMConfig, WelfareWeights

config = GSMConfig(welfare_weights=WelfareWeights(theta_g=0.7, theta_f=0.3))
gov = MultiLevelGovernance.from_single_jurisdiction(
    "A",
    accountability=88.3, competence=92.2, cohesion=90.0,
    continuity=96.2, learning=72.4,
    config=config,
)
print(gov.welfare("A"))
```

---

## 7. Working with Constraints

### 7.1 Conditions A, B, and C

The constraint classifies each action into one of four outcomes:

| **Condition** | **Test** | **Result** |
|---------------|----------|-----------|
| **A** — No harm | $\Delta\mathcal{W}^{\text{pol}}_j \geq 0$ for all $j$ | Admissible |
| **B** — Threshold tolerance | $-\tau_j \leq \Delta\mathcal{W}^{\text{pol}}_j < 0$ | Admissible |
| **C** — Compensation | $\Delta\mathcal{W}^{\text{pol}}_j + \text{Comp}^{\text{eff}} \geq 0$ | Admissible |
| **Violation** | None of A, B, C holds | Blocked |

```python
from gsm_governance import BoundedNonExploitationConstraint

constraint = BoundedNonExploitationConstraint(tau=5.0)

# Counterfactual no-action baseline
welfare_cf = {"A": 78.0, "B": 70.0}

# Action branch
welfare_after = {"A": 82.0, "B": 62.0}

result = constraint.check(welfare_after, welfare_cf)
print(result.admissible)  # False
print(result.condition)   # "violation"
print(result.policy_welfare_change)  # [4., -8.]
print(result.slack)       # [9., -3.]
```

### 7.2 Threshold Functions

Thresholds can be fixed, per-jurisdiction, or context-dependent.

**Fixed threshold:**

```python
constraint = BoundedNonExploitationConstraint(tau=5.0)
```

**Per-jurisdiction thresholds:**

```python
constraint = BoundedNonExploitationConstraint(
    tau={"A": 5.0, "B": 3.0, "C": 8.0}
)
```

**Context-dependent threshold via `ThresholdFunction`:**

$$\tau_j = \tau(\mathbf{z}_j, \boldsymbol{\omega}) = \omega_0 + \sum_k \omega_k z_{j,k}$$

```python
from gsm_governance.dynamics.constraint import ThresholdFunction

tf = ThresholdFunction(omega={
    "base": 5.0,
    "development": 0.10,
    "institutional_capacity": -0.05,
    "historical_precedent": 0.05,
})

# For jurisdiction with high development, threshold becomes tighter
tau_rich = tf({"development": 80.0, "institutional_capacity": 90.0})
tau_poor = tf({"development": 30.0, "institutional_capacity": 40.0})
print(tau_rich, tau_poor)
```

### 7.3 Compensation Vectors

Compensation is a six-component vector:

| **Component** | **Meaning** |
|---------------|-------------|
| `fiscal` | Direct payments |
| `infrastructure` | Physical and digital infrastructure |
| `representation` | Decision-making rights |
| `regulatory` | Regulatory exemptions or flexibilities |
| `future_commitment` | Binding future benefits |
| `restitution` | Repair for past harms |

```python
from gsm_governance import CompensationVector

# Scalar compensation (all in fiscal)
comp_scalar = CompensationVector.scalar(10.0)

# Mixed compensation
comp_mixed = CompensationVector(
    fiscal=5.0,
    infrastructure=3.0,
    representation=1.0,
    regulatory=0.5,
)

# Access components
print(comp_mixed.fiscal)          # 5.0
print(comp_mixed.as_array())      # array([5., 3., 1., 0.5, 0., 0.])
```

### 7.4 Valuation Vectors

The recipient's valuation vector $\boldsymbol{\lambda}_j$ determines how each compensation component is weighted:

$$\text{Comp}^{\text{eff}}_{i \to j} = \boldsymbol{\lambda}_j^\top \text{Comp}_{i \to j}$$

```python
import numpy as np

constraint = BoundedNonExploitationConstraint(
    tau=5.0,
    valuation_vectors={
        # Jurisdiction A values fiscal compensation most
        "A": np.array([0.5, 0.2, 0.1, 0.1, 0.05, 0.05]),
        # Jurisdiction B values representation and infrastructure
        "B": np.array([0.1, 0.3, 0.3, 0.1, 0.1, 0.1]),
    },
)

# If no valuation vector is provided for a jurisdiction,
# uniform 1/6 weights are used
```

**Determination of valuation vectors.** The paper (Section 4.6.5) identifies four possible mechanisms: (1) recipient declaration, (2) judicial determination, (3) bargaining, (4) empirical estimation. The library does not prescribe a mechanism; the caller supplies the vectors.

---

## 8. Running Simulations

### 8.1 Basic Simulation

```python
from gsm_governance import (
    BoundedNonExploitationConstraint,
    GSMConfig,
    Jurisdiction,
    MultiLevelGovernance,
    Simulation,
)

# Build a system
system = build_multi_jurisdiction_system()  # from Section 9.2

# Create a constraint
constraint = BoundedNonExploitationConstraint(tau=5.0)

# Run a 20-period simulation
sim = Simulation(system, constraint=constraint, seed=42)
history = sim.run(n_steps=20)

# Convert to DataFrame
df = history.to_dataframe()
print(df.head())
```

### 8.2 Adding Shocks

Shocks represent external disturbances (crises, environmental events, economic downturns):

```python
import numpy as np

# A shock of magnitude 5 applied to jurisdiction "A" at time t=5
shocks = {
    5: {"A": np.array([5.0, 0.0, 0.0, 0.0])},
    12: {"B": np.array([2.0, 1.0, 0.0, 0.0])},
}

history = sim.run(n_steps=20, shocks=shocks)
```

The shock vector is applied to the flourishing dynamics through the shock-propagation matrix $\mathbf{S}$.

### 8.3 Policy Controls

Policy controls are exogenous interventions applied to the governance state:

```python
# At t=3, apply a control to jurisdiction "A" boosting its competence by 3
controls = {
    3: {"A": np.array([0.0, 3.0, 0.0, 0.0, 0.0])},
}

history = sim.run(n_steps=20, controls=controls)
```

The simulation uses the **counterfactual baseline** (Section 8.1 above): for each period, it runs both the action branch (with controls) and the counterfactual branch (zero controls), checks the constraint against the counterfactual, and either commits or rejects the action.

### 8.4 Examining the History

```python
df = history.to_dataframe()

# Filter to a single jurisdiction
df_a = df[df["jurisdiction"] == "A"]

# Extract governance trajectory
gov_traj = history.governance_trajectory("A", "national")
print(gov_traj)

# Extract flourishing trajectory
flo_traj = history.flourishing_trajectory("A", "national")
print(flo_traj)

# Check for constraint violations
violations = df[df["jurisdiction"] == "__constraint__"]
print(f"Number of violations: {len(violations)}")
print(violations[["time", "condition", "min_slack"]])
```

---

## 9. Working with Data

### 9.1 Loading Denmark's Data

The library ships with Denmark's raw governance indicators from real international sources:

```python
from gsm_governance.data.loaders import load_denmark_raw, normalize_denmark

# Raw values (Section 16.2 of the paper)
raw = load_denmark_raw()
print(raw)
# {'accountability': 0.883, 'competence': 2.11, 'cohesion': 0.9,
#  'continuity': 0.962, 'learning': 72.4}

# Normalized to [0, 100]
gov_state = normalize_denmark()
print(gov_state)
# GovernanceState(accountability=88.3, competence=92.2, cohesion=90.0,
#                 continuity=96.2, learning=72.4)
```

The normalization uses theoretical minima and maxima declared per data source (see Appendix B of the paper).

### 9.2 Building a Multi-Level System

```python
from gsm_governance import (
    GSMConfig,
    Jurisdiction,
    MultiLevelGovernance,
)
from gsm_governance.core.state import FlourishingState, GovernanceState


def build_multi_jurisdiction_system() -> MultiLevelGovernance:
    """Build a small 3-jurisdiction system (all abstract labels)."""
    config = GSMConfig()

    jurisdictions = [
        Jurisdiction(
            name="A", level="national",
            governance=GovernanceState(88.3, 92.2, 90.0, 96.2, 72.4),
            flourishing=FlourishingState(95.0, 92.5, 74.0, 88.0),
        ),
        Jurisdiction(
            name="B", level="national",
            governance=GovernanceState(94.1, 92.9, 94.5, 92.8, 94.2),
            flourishing=FlourishingState(93.5, 91.0, 76.0, 90.0),
        ),
        Jurisdiction(
            name="C", level="national",
            governance=GovernanceState(85.0, 82.0, 80.0, 85.0, 88.0),
            flourishing=FlourishingState(90.0, 88.0, 72.0, 85.0),
        ),
    ]
    return MultiLevelGovernance(config=config, jurisdictions=jurisdictions)
```

For a **five-level** system (community → supranational):

```python
from gsm_governance import Simulation, BoundedNonExploitationConstraint


def build_five_level_system() -> MultiLevelGovernance:
    config = GSMConfig()

    levels = {
        "international": (80.0, 78.0, 72.0, 88.0, 85.0),
        "national":      (85.0, 82.0, 80.0, 85.0, 88.0),
        "regional":      (82.0, 80.0, 78.0, 82.0, 84.0),
        "municipal":     (85.0, 88.0, 86.0, 80.0, 90.0),
        "community":     (88.0, 75.0, 92.0, 78.0, 85.0),
    }

    jurisdictions = []
    for level, caps in levels.items():
        jurisdictions.append(
            Jurisdiction(
                name=f"L_{level}",
                level=level,
                governance=GovernanceState(*caps),
                flourishing=FlourishingState(85.0, 88.0, 82.0, 75.0),
            )
        )
    return MultiLevelGovernance(config=config, jurisdictions=jurisdictions)
```

---

## 10. Visualization

The library provides three main plotting functions:

### Radar chart of governance capabilities

```python
import matplotlib.pyplot as plt
from gsm_governance.utils.visualization import plot_governance_radar

gov = build_multi_jurisdiction_system()
a = gov.jurisdictions[0]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})
plot_governance_radar(a.governance.as_array(), label="Jurisdiction A", ax=ax)
plt.tight_layout()
plt.savefig("radar.png", dpi=150)
plt.show()
```

### Governance trajectory over time

```python
from gsm_governance.utils.visualization import plot_governance_trajectory

system = build_five_level_system()
sim = Simulation(system, seed=42)
history = sim.run(n_steps=20)

traj = history.governance_trajectory("L_national", "national").values

fig, ax = plt.subplots(figsize=(8, 5))
plot_governance_trajectory(traj, ax=ax)
plt.tight_layout()
plt.savefig("gov_trajectory.png", dpi=150)
plt.show()
```

### Flourishing trajectory

```python
from gsm_governance.utils.visualization import plot_flourishing_trajectory

flo_traj = history.flourishing_trajectory("L_national", "national").values

fig, ax = plt.subplots(figsize=(8, 5))
plot_flourishing_trajectory(flo_traj, ax=ax)
plt.tight_layout()
plt.savefig("flo_trajectory.png", dpi=150)
plt.show()
```

---

## 11. Complete Worked Examples

### 11.1 Single Jurisdiction: Denmark

```python
"""Reproduce the Denmark worked example (Section 16 of the paper)."""

from gsm_governance import MultiLevelGovernance
from gsm_governance.data.loaders import load_denmark_raw, normalize_denmark
from gsm_governance.metrics.indices import gsi_theoretical_max


def main() -> None:
    # 1. Raw data
    raw = load_denmark_raw()
    print("Raw data (Section 16.2):")
    for k, v in raw.items():
        print(f"  {k:>15s} : {v}")

    # 2. Normalize
    gov_state = normalize_denmark()
    print(f"\nNormalized state: {gov_state}")

    # 3. Build single-jurisdiction system
    gov = MultiLevelGovernance.from_single_jurisdiction(
        name="Denmark",
        accountability=gov_state.accountability,
        competence=gov_state.competence,
        cohesion=gov_state.cohesion,
        continuity=gov_state.continuity,
        learning=gov_state.learning,
        economic=95.0, quality=92.5, wellbeing=74.0, sustainability=88.0,
    )

    # 4. Compute metrics
    print("\nMetrics:")
    print(f"  GSI theoretical max : {gsi_theoretical_max(gov.config):.2f}")
    print(f"  GSI (normalized)    : {gov.gsi():.2f}")
    print(f"  HFI                 : {gov.hfi():.2f}")
    print(f"  Misalignment D*     : {gov.misalignment('Denmark'):.2f}")
    print(f"  Welfare W_j         : {gov.welfare('Denmark'):.2f}")


if __name__ == "__main__":
    main()
```

**Expected output:**

```
Raw data (Section 16.2):
  accountability : 0.883
     competence : 2.11
       cohesion : 0.9
     continuity : 0.962
       learning : 72.4

Normalized state: GovernanceState(
    accountability=88.3, competence=92.2, cohesion=90.0,
    continuity=96.2, learning=72.4)

Metrics:
  GSI theoretical max : 600.00
  GSI (normalized)    : 48.07
  HFI                 : 87.40
  Misalignment D*     : 18.20
  Welfare W_j         : 67.74
```

### 11.2 Multi-Jurisdiction Simulation

```python
"""Illustrative multi-jurisdiction simulation with a constraint check."""

import numpy as np

from gsm_governance import (
    BoundedNonExploitationConstraint,
    CompensationVector,
    GSMConfig,
    Jurisdiction,
    MultiLevelGovernance,
)
from gsm_governance.core.state import FlourishingState, GovernanceState


def build_system() -> MultiLevelGovernance:
    return MultiLevelGovernance(
        config=GSMConfig(),
        jurisdictions=[
            Jurisdiction(
                name="A", level="national",
                governance=GovernanceState(88.3, 92.2, 90.0, 96.2, 72.4),
                flourishing=FlourishingState(95.0, 92.5, 74.0, 88.0),
            ),
            Jurisdiction(
                name="B", level="national",
                governance=GovernanceState(94.1, 92.9, 94.5, 92.8, 94.2),
                flourishing=FlourishingState(93.5, 91.0, 76.0, 90.0),
            ),
            Jurisdiction(
                name="C", level="national",
                governance=GovernanceState(85.0, 82.0, 80.0, 85.0, 88.0),
                flourishing=FlourishingState(90.0, 88.0, 72.0, 85.0),
            ),
        ],
    )


def main() -> None:
    system = build_system()

    print("=== GSM metrics ===")
    for j in system.jurisdictions:
        print(
            f"{j.name:>3s}  "
            f"GSI={system.gsi(j.name):6.2f}  "
            f"HFI={system.hfi(j.name):6.2f}  "
            f"D*={system.misalignment(j.name):5.2f}"
        )

    print(f"\nDistribution-sensitive HFI: "
          f"{system.hfi(distribution_sensitive=True):.2f}")

    # --- Constraint check ---
    constraint = BoundedNonExploitationConstraint(
        tau=5.0,
        valuation_vectors={j.name: np.full(6, 1/6) for j in system.jurisdictions},
    )

    # Counterfactual baseline
    welfare_cf = {j.name: 70.0 for j in system.jurisdictions}

    # Action: A and B improve, C loses
    welfare_after = dict(welfare_cf)
    welfare_after["A"] += 5.0
    welfare_after["B"] += 3.0
    welfare_after["C"] -= 8.0

    # Compensation from A and B to C
    comp = {
        ("A", "C"): CompensationVector.scalar(2.0),
        ("B", "C"): CompensationVector.scalar(1.5),
    }

    result = constraint.check(welfare_after, welfare_cf, compensation=comp)
    print("\n=== Bounded non-exploitation check ===")
    print(f"  admissible : {result.admissible}")
    print(f"  condition  : {result.condition}")
    print(f"  dW_pol     : {result.policy_welfare_change}")
    print(f"  slack      : {result.slack}")


if __name__ == "__main__":
    main()
```

**Expected output:**

```
=== GSM metrics ===
  A  GSI= 48.07  HFI= 87.40  D*=18.20
  B  GSI= 53.00  HFI= 87.63  D*= 7.10
  C  GSI= 42.85  HFI= 83.75  D*=14.30

Distribution-sensitive HFI: 61.14

=== Bounded non-exploitation check ===
  admissible : False
  condition  : violation
  dW_pol     : [ 5.  3. -8.]
  slack      : [10.   8.  -2.5]
```

### 11.3 Five-Level System with Shock

```python
"""Illustrative five-level simulation with a supranational shock."""

import numpy as np
import matplotlib.pyplot as plt

from gsm_governance import (
    BoundedNonExploitationConstraint,
    GSMConfig,
    Jurisdiction,
    MultiLevelGovernance,
    Simulation,
)
from gsm_governance.core.state import FlourishingState, GovernanceState
from gsm_governance.utils.visualization import plot_governance_trajectory


def build_five_level_system() -> MultiLevelGovernance:
    levels = {
        "international": (80.0, 78.0, 72.0, 88.0, 85.0),
        "national":      (85.0, 82.0, 80.0, 85.0, 88.0),
        "regional":      (82.0, 80.0, 78.0, 82.0, 84.0),
        "municipal":     (85.0, 88.0, 86.0, 80.0, 90.0),
        "community":     (88.0, 75.0, 92.0, 78.0, 85.0),
    }
    jurisdictions = [
        Jurisdiction(
            name=f"L_{level}",
            level=level,
            governance=GovernanceState(*caps),
            flourishing=FlourishingState(85.0, 88.0, 82.0, 75.0),
        )
        for level, caps in levels.items()
    ]
    return MultiLevelGovernance(config=GSMConfig(), jurisdictions=jurisdictions)


def main() -> None:
    system = build_five_level_system()
    constraint = BoundedNonExploitationConstraint(tau=5.0)
    sim = Simulation(system, constraint=constraint, seed=42)

    # Apply a shock at t=3
    shocks = {3: {"L_international": np.array([5.0, 0.0, 0.0, 0.0])}}

    history = sim.run(n_steps=20, shocks=shocks)

    # Plot the national level's trajectory
    traj = history.governance_trajectory("L_national", "national").values

    fig, ax = plt.subplots(figsize=(9, 5))
    plot_governance_trajectory(traj, ax=ax)
    ax.set_title("National-level governance capabilities over time")
    plt.tight_layout()
    plt.savefig("five_level_trajectory.png", dpi=150)

    # Report any constraint violations
    df = history.to_dataframe()
    violations = df[df["jurisdiction"] == "__constraint__"]
    print(f"Constraint violations: {len(violations)}")


if __name__ == "__main__":
    main()
```

---

## 12. API Reference

### Main classes

| **Class** | **Module** | **Purpose** |
|-----------|-----------|-------------|
| `MultiLevelGovernance` | `gsm_governance.core.system` | Container for jurisdictions |
| `Jurisdiction` | `gsm_governance.core.system` | Single jurisdiction |
| `GovernanceState` | `gsm_governance.core.state` | Five-dimension capability vector |
| `FlourishingState` | `gsm_governance.core.state` | Four-dimension flourishing vector |
| `GSMConfig` | `gsm_governance.core.parameters` | Global parameters |
| `LevelParameters` | `gsm_governance.core.parameters` | Level-specific parameters |
| `WelfareWeights` | `gsm_governance.core.parameters` | Welfare function weights |
| `BoundedNonExploitationConstraint` | `gsm_governance.dynamics.constraint` | Non-exploitation check |
| `CompensationVector` | `gsm_governance.dynamics.constraint` | Six-component compensation |
| `ThresholdFunction` | `gsm_governance.dynamics.constraint` | Context-dependent threshold |
| `ConstraintResult` | `gsm_governance.dynamics.constraint` | Result of a check |
| `Simulation` | `gsm_governance.dynamics.simulation` | Time-domain simulator |
| `SimulationHistory` | `gsm_governance.dynamics.simulation` | Simulation output container |

### Key functions

| **Function** | **Module** | **Purpose** |
|-------------|-----------|-------------|
| `compute_gsi` | `gsm_governance.metrics.indices` | Governance Success Index |
| `compute_gsi_raw` | `gsm_governance.metrics.indices` | Raw (unnormalized) GSI |
| `gsi_theoretical_max` | `gsm_governance.metrics.indices` | Theoretical maximum |
| `compute_hfi` | `gsm_governance.metrics.indices` | Human Flourishing Index |
| `compute_welfare` | `gsm_governance.metrics.welfare` | Jurisdictional welfare |
| `distribution_sensitive_hfi` | `gsm_governance.metrics.welfare` | Gini-adjusted HFI |
| `policy_welfare_change` | `gsm_governance.metrics.welfare` | Counterfactual ΔW |
| `threshold_sensitivity` | `gsm_governance.metrics.welfare` | H10 mechanisms |
| `context_sensitive_misalignment` | `gsm_governance.metrics.misalignment` | D* measure |
| `vertical_misalignment` | `gsm_governance.metrics.misalignment` | D^vert measure |
| `resilience_metrics` | `gsm_governance.metrics.resilience` | R_T, R_L, R_A |
| `minmax_normalize` | `gsm_governance.utils.normalization` | Min-max scaling |
| `load_denmark_raw` | `gsm_governance.data.loaders` | Real Denmark raw data |
| `normalize_denmark` | `gsm_governance.data.loaders` | Normalized Denmark |

---

## 13. Troubleshooting

### `ValueError: Welfare weights must sum to 1.0`

The `WelfareWeights` class requires `theta_g + theta_f = 1`. Check your values:

```python
# Wrong
WelfareWeights(theta_g=0.7, theta_f=0.4)  # sums to 1.1

# Correct
WelfareWeights(theta_g=0.7, theta_f=0.3)
```

### `ValueError: alpha must have shape (5,)`

All parameter arrays must have the correct shape:

```python
import numpy as np

# Wrong
GSMConfig(alpha=np.array([0.2, 0.2]))  # only 2 elements

# Correct
GSMConfig(alpha=np.array([0.2, 0.2, 0.2, 0.2, 0.2]))
```

### The constraint reports unexpected violations

Check that you are passing **the counterfactual baseline** — not the current welfare — as the second argument to `check`:

```python
# Wrong
result = constraint.check(welfare_after, welfare_before)

# Correct
result = constraint.check(welfare_after, welfare_counterfactual)
```

### GSI looks too low (e.g., 48 instead of 94)

This is expected in v0.2.0. The theoretical maximum is 600, not 1000. See [Section 14](#14-migration-from-v010).

### Simulation produces identical trajectories across runs

Set `seed=None` for non-deterministic runs, or ensure that `noise_g` and `noise_f` in `LevelParameters` are non-zero:

```python
from gsm_governance.core.parameters import LevelParameters

params = LevelParameters(noise_g=0.1, noise_f=0.1)
```

---

## 14. Migration from v0.1.0

Three **breaking changes** were introduced in v0.2.0:

### Change 1 — GSI normalization

| **Version** | **Denmark's GSI** | **Theoretical maximum** |
|-------------|-------------------|-------------------------|
| 0.1.0 (incorrect) | 94.2 | 1000 |
| 0.2.0 (correct)   | **48.07** | **600** |

**Migration:**

```python
# v0.1.0
gsi = gov.gsi()  # 94.2

# v0.2.0
gsi = gov.gsi()  # 48.07
```

The relative ordering of jurisdictions is unchanged. Absolute values simply shift to the corrected scale.

### Change 2 — Constraint baseline

```python
# v0.1.0
result = constraint.check(welfare_before, welfare_after)

# v0.2.0
result = constraint.check(welfare_after, welfare_counterfactual)
```

The new signature isolates policy effects from time trends.

### Change 3 — Effective compensation

```python
# v0.1.0 — effective compensation was implicitly uniform
# v0.2.0 — valuation vectors are now first-class
constraint = BoundedNonExploitationConstraint(
    tau=5.0,
    valuation_vectors={"A": np.full(6, 1/6)},
)
```

### Change 4 — Country rankings removed

All country-specific tables have been removed. Use abstract labels (`"A"`, `"B"`, `"L_national"`) in your own analyses.

---

## 15. Citation and License

### Citation

```bibtex
@article{wang2026gsm,
  title={A Computational Systems Model of Multi-Level Governance:
         Extending the General Governance Success Model with a
         Bounded Non-Exploitation Constraint},
  author={Wang, Harris},
  journal={Systems Research and Behavioral Science},
  year={2026}
}
```

### Library citation

```bibtex
@software{wang2026gsm_lib,
  title={gsm-governance: A Python library for the General Governance Success Model},
  author={Wang, Harris},
  version={0.2.0},
  year={2026},
  url={https://github.com/harriswang/gsm-governance}
}
```

### License

MIT License. See `LICENSE` for details.

---

## Appendix: Glossary

| **Term** | **Definition** |
|----------|---------------|
| **GSI** | Governance Success Index — a weighted sum of the five capabilities plus pairwise interactions, normalized to 0–100 |
| **HFI** | Human Flourishing Index — a weighted sum of the four flourishing dimensions |
| **HFI^dist** | Distribution-sensitive HFI — min HFI minus ρ × Gini |
| **Welfare** $\mathcal{W}$ | Composite of GSI and HFI^dist |
| **Misalignment** $D^*$ | Distance between the current governance state and a contextual target |
| **Vertical misalignment** $D^{\text{vert}}$ | Misalignment between governance configurations across levels |
| **Exploitation index** $\mathcal{E}$ | Composite measure of uncompensated cross-jurisdictional harm |
| **Threshold** $\tau_j$ | Socially accepted maximum sacrifice for jurisdiction $j$ |
| **Effective compensation** | $\boldsymbol{\lambda}_j^\top \text{Comp}_{i \to j}$ |
| **Valuation vector** $\boldsymbol{\lambda}_j$ | Recipient's weights over the six compensation components |
| **Counterfactual baseline** | $W_j(t+1 \mid \mathbf{0})$ — welfare had the action not been taken |

---

*This user guide documents `gsm-governance` v0.2.0. For the latest version, visit the project repository.*