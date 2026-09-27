# gsm-governance

> A Python library for computational modelling of multi-level governance with a bounded non-exploitation constraint.

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](https://github.com/harriswang/gsm-governance/releases)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](#project-status)
[![DOI](https://img.shields.io/badge/DOI-10.20944%2Fpreprints202609.0233.v1-blue)](https://doi.org/10.20944/preprints202609.0233.v2)

---

## Overview

`gsm-governance` implements the **General Governance Success Model (GSM)** — a systems-theoretical framework that represents governance as a complex adaptive system composed of five coupled capabilities operating across nested levels, subject to a **bounded non-exploitation constraint** that prevents any jurisdiction from imposing uncompensated, non-trivial sacrifices on others for its own benefit.

The library provides:

- **Multi-level governance dynamics** — community → municipal → regional → national → supranational
- **Five-dimension governance model** — accountability, competence, cohesion, continuity, learning
- **Four-dimension flourishing model** — economic, quality, well-being, sustainability
- **Bounded non-exploitation constraint** with threshold tolerance and vector-valued compensation
- **Time-domain simulation** with shocks, policy controls, and counterfactual baselines
- **Comprehensive metrics** — GSI, HFI, misalignment, welfare, resilience, exploitation
- **Data loaders** for real indicators from V-Dem, World Bank WGI, WJP, UNDP, and OWID
- **Visualization utilities** for radar charts, trajectories, and constraint checks

Based on:

> Wang, H. (2026). *A Computational Systems Model of Multi-Level Governance for Human Flourishing under Bounded Non-Exploitation Constraint.* preprint.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Features](#features)
- [Examples](#examples)
- [Documentation](#documentation)
- [Project Status](#project-status)
- [Citation](#citation)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Installation

### From PyPI (once released)

```bash
pip install gsm-governance
```

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

### Requirements

- Python ≥ 3.9
- NumPy ≥ 1.22
- SciPy ≥ 1.9
- pandas ≥ 1.5
- matplotlib ≥ 3.6

### Verify installation

```python
import gsm_governance
print(gsm_governance.__version__)  # "0.2.0"
```

---

## Quick Start

```python
from gsm_governance import MultiLevelGovernance

# Create a single jurisdiction with real Denmark governance indicators
gov = MultiLevelGovernance.from_single_jurisdiction(
    name="Denmark",
    accountability=88.3,   # normalized V-Dem score
    competence=92.2,       # normalized World Bank WGI score
    cohesion=90.0,         # normalized WJP Rule of Law Index
    continuity=96.2,       # normalized UNDP HDI
    learning=72.4,         # Government Service Satisfaction
    economic=95.0, quality=92.5, wellbeing=74.0, sustainability=88.0,
)

# Compute governance and flourishing indices
print(f"GSI : {gov.gsi():.2f}")                    # 48.07
print(f"HFI : {gov.hfi():.2f}")                    # 87.40
print(f"D*  : {gov.misalignment('Denmark'):.2f}")  # 18.20
print(f"W   : {gov.welfare('Denmark'):.2f}")       # 67.74
```

> **Note on the GSI scale.** In version 0.2.0, the theoretical maximum of the raw GSI is **600** (not 1000 as in earlier versions), so Denmark's normalized GSI is **48.07**. See the [Migration Guide](docs/migration.md) for details.

---

## Core Concepts

### The Five Governance Capabilities

| Capability | Symbol | Example indicator |
|------------|--------|-------------------|
| Accountability | `a` | V-Dem Liberal Democracy Index |
| Competence | `c` | World Bank Government Effectiveness |
| Cohesion | `s` | WJP Rule of Law Index |
| Continuity | `r` | UNDP Human Development Index |
| Learning | `ℓ` | Government Service Satisfaction |

### The Four Flourishing Dimensions

| Dimension | Symbol | Example indicator |
|-----------|--------|-------------------|
| Economic | `e` | GNI per capita (PPP) |
| Quality | `q` | Life expectancy / education |
| Well-being | `w` | Social trust |
| Sustainability | `n` | Environmental performance |

### The Bounded Non-Exploitation Constraint

An action by jurisdiction $i$ is **admissible** if, for every other jurisdiction $j$, at least one of the following conditions holds:

- **Condition A** — No harm: $\Delta \mathcal{W}_j^{\text{pol}} \geq 0$
- **Condition B** — Threshold tolerance: $\Delta \mathcal{W}_j^{\text{pol}} \geq -\tau_j$
- **Condition C** — Compensation: $\Delta \mathcal{W}_j^{\text{pol}} + \boldsymbol{\lambda}_j^\top \text{Comp}_{i \to j} \geq 0$

where $\Delta \mathcal{W}_j^{\text{pol}} = \mathcal{W}_j(t+1 \mid \mathbf{u}) - \mathcal{W}_j(t+1 \mid \mathbf{0})$ is the **policy-induced welfare change** relative to a counterfactual no-action baseline.

---

## Features

### 1. Multi-level system construction

```python
from gsm_governance import GSMConfig, Jurisdiction, MultiLevelGovernance
from gsm_governance.core.state import FlourishingState, GovernanceState

system = MultiLevelGovernance(
    config=GSMConfig(),
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

### 2. Computing indices

```python
print(system.gsi("A"))
print(system.hfi("A"))
print(system.hfi(distribution_sensitive=True))  # Gini-adjusted across all jurisdictions
print(system.misalignment("A"))
print(system.welfare("A"))
```

### 3. Bounded non-exploitation constraint

```python
import numpy as np
from gsm_governance import BoundedNonExploitationConstraint, CompensationVector

constraint = BoundedNonExploitationConstraint(
    tau=5.0,
    valuation_vectors={"A": np.full(6, 1/6), "B": np.full(6, 1/6)},
)

welfare_cf = {"A": 78.0, "B": 70.0}      # counterfactual no-action
welfare_after = {"A": 82.0, "B": 62.0}   # with action

comp = {("A", "B"): CompensationVector.scalar(18.0)}

result = constraint.check(welfare_after, welfare_cf, compensation=comp)
print(result.admissible)          # True
print(result.condition)           # "C"
print(result.policy_welfare_change)  # [ 4., -8.]
print(result.slack)               # [9., 1.]
```

### 4. Time-domain simulation

```python
import numpy as np
from gsm_governance import Simulation

sim = Simulation(system, constraint=constraint, seed=42)

shocks = {3: {"A": np.array([5.0, 0.0, 0.0, 0.0])}}
history = sim.run(n_steps=20, shocks=shocks)

df = history.to_dataframe()
gov_traj = history.governance_trajectory("A", "national")
flo_traj = history.flourishing_trajectory("A", "national")
```

### 5. Loading real governance data

```python
from gsm_governance.data.loaders import load_denmark_raw, normalize_denmark

raw = load_denmark_raw()       # real V-Dem / WGI / WJP / UNDP / OWID values
gov_state = normalize_denmark()  # normalized to [0, 100]
```

### 6. Visualization

```python
import matplotlib.pyplot as plt
from gsm_governance.utils.visualization import (
    plot_governance_radar,
    plot_governance_trajectory,
    plot_flourishing_trajectory,
)

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})
plot_governance_radar(system.jurisdictions[0].governance.as_array(), ax=ax)
plt.savefig("radar.png", dpi=150)
```

---

## Examples

The `examples/` directory contains three complete, runnable scripts:

| **Script** | **Description** |
|------------|-----------------|
| [`denmark_worked_example.py`](examples/denmark_worked_example.py) | Reproduce the Denmark worked example (Section 16 of the paper) |
| [`multi_country_analysis.py`](examples/multi_country_analysis.py) | Illustrative multi-jurisdiction constraint check using abstract jurisdictions A–E |
| [`five_level_simulation.py`](examples/five_level_simulation.py) | Five-level simulation with a supranational shock |

Run any example with:

```bash
python examples/denmark_worked_example.py
```

### Expected output from `denmark_worked_example.py`

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

---

## Documentation

| **Resource** | **Description** |
|--------------|-----------------|
| [User Guide](docs/user-guide.md) | Comprehensive walkthrough with examples |
| [API Reference](docs/api-reference.md) | Complete class and function documentation |
| [Migration Guide](docs/migration.md) | Breaking changes between v0.1.0 and v0.2.0 |
| [Theory Background](docs/theory.md) | Formal model and equations |
| [Data Sources](docs/data-sources.md) | V-Dem, WGI, WJP, UNDP, OWID provenance |

### In-repo documentation

- [`docs/user-guide.md`](docs/user-guide.md) — Full 15-section user guide
- [`docs/api-reference.md`](docs/api-reference.md) — Auto-generated API docs
- [`docs/migration.md`](docs/migration.md) — Version migration notes
- [`docs/theory.md`](docs/theory.md) — Mathematical foundations

---

## Package Structure

```
gsm-governance/
├── gsm_governance/
│   ├── core/               # State, parameters, multi-level system
│   │   ├── parameters.py
│   │   ├── state.py
│   │   └── system.py
│   ├── dynamics/           # Transitions, simulation, constraint
│   │   ├── constraint.py
│   │   ├── simulation.py
│   │   └── transitions.py
│   ├── metrics/            # GSI, HFI, misalignment, welfare, resilience
│   │   ├── indices.py
│   │   ├── misalignment.py
│   │   ├── resilience.py
│   │   └── welfare.py
│   ├── data/               # Data loaders for external sources
│   │   ├── loaders.py
│   │   └── sources.py
│   └── utils/              # Normalization and visualization
│       ├── normalization.py
│       └── visualization.py
├── examples/               # Runnable example scripts
├── tests/                  # Unit tests
├── docs/                   # Extended documentation
├── pyproject.toml
├── CHANGELOG.md
├── LICENSE
└── README.md
```

---

## Project Status

**Current version: 0.2.0 (alpha)**

The library is under active development. The following are known limitations:

- **Empirical calibration is not yet complete.** The default parameters ($\alpha_i = 0.2$, $\kappa_{ij} = 0.005$, $\gamma_k = 0.25$) are illustrative, not empirically estimated. Users doing serious empirical work should estimate these parameters from their own data.
- **Exploitation index $\mathcal{E}$ is not yet operationalized.** The library provides the constraint machinery but does not currently ship with an implementation of the exploitation index. A roadmap is provided in Section 15.7 of the paper.
- **Valuation vector determination is caller-supplied.** The library does not prescribe how $\boldsymbol{\lambda}_j$ should be determined; users supply it directly.
- **Country-specific rankings are intentionally absent.** The library does not ship with country rankings or benchmarks, since these require empirical estimation beyond the current scope.

### Roadmap

| **Version** | **Planned features** |
|-------------|---------------------|
| 0.3.0 | Empirical calibration utilities (Bayesian hierarchical estimation) |
| 0.4.0 | Exploitation index operationalization (env, fiscal, regulatory, institutional, temporal) |
| 0.5.0 | Agent-based simulation backend |
| 0.6.0 | Interaction with external governance databases via APIs |
| 1.0.0 | Stable API, published empirical benchmarks, peer-reviewed validation |

---

## Citation

If you use this library in academic work, please cite both the paper and the software:

### Paper

```bibtex
@article{wang2026gsm,
  title={A Computational Systems Model of Multi-Level Governance:
         Extending the General Governance Success Model with a
         Bounded Non-Exploitation Constraint},
  author={Wang, Harris},
  journal={Systems Research and Behavioral Science},
  year={2026},
  doi={10.20944/preprints202609.0233.v1}
}
```

### Software

```bibtex
@software{wang2026gsm_lib,
  title={gsm-governance: A Python library for the General Governance Success Model},
  author={Wang, Harris},
  version={0.2.0},
  year={2026},
  url={https://github.com/harriswang/gsm-governance}
}
```

---

## Contributing

Contributions are welcome. To contribute:

1. **Fork the repository** and create a feature branch:

   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Install development dependencies:**

   ```bash
   pip install -e ".[dev]"
   ```

3. **Run the test suite:**

   ```bash
   pytest tests/
   ```

4. **Follow the code style:**

   ```bash
   black gsm_governance/
   ruff check gsm_governance/
   mypy gsm_governance/
   ```

5. **Commit and push** to your fork:

   ```bash
   git commit -am "Add my new feature"
   git push origin feature/my-new-feature
   ```

6. **Open a Pull Request** with a clear description of the change.

### Areas where contributions are especially welcome

- **Empirical calibration** — Bayesian estimation of $\alpha_i$, $\kappa_{ij}$, $\gamma_k$
- **Exploitation index implementation** — operationalizing the five-component roadmap
- **Additional visualization** — causal-loop diagrams, network plots, Sankey diagrams
- **Tests** — edge cases for the constraint, misalignment, and resilience metrics
- **Documentation** — tutorials, worked examples, translations
- **Cross-validation** — validating the library against independent implementations

Please open an [issue](https://github.com/harriswang/gsm-governance/issues) before starting substantial work so we can coordinate.

### Reporting bugs

When filing a bug report, please include:

- Python version
- `gsm_governance.__version__`
- A minimal reproducible example
- The full traceback, if applicable

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

```
MIT License

Copyright (c) 2026 Harris Wang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

---

## Acknowledgements

This library builds on several intellectual traditions:

- **Cybernetics and the Viable System Model** — Stafford Beer, W. Ross Ashby, Heinz von Foerster
- **System Dynamics** — Jay Forrester, Donella Meadows, John Sterman
- **Polycentric Governance** — Elinor Ostrom, Vincent Ostrom
- **Multi-Level Governance** — Liesbet Hooghe, Gary Marks
- **Complex Adaptive Governance** — C. S. Holling, Carl Folke, Simon Levin
- **Distributive Justice** — John Rawls, Amartya Sen, Martha Nussbaum, David Miller, Iris Marion Young
- **Critical Systems Thinking** — Michael C. Jackson, Gerald Midgley, Werner Ulrich

The author thanks the anonymous reviewers at *Systems Research and Behavioral Science* for their careful and constructive feedback across multiple rounds of revision.

---

## Contact

- **Author** — Harris Wang, Athabasca University (harrisw@athabascau.ca)
- **Issues** — [github.com/harriswang/gsm-governance/issues](https://github.com/harriswang/gsm-governance/issues)
- **Discussions** — [github.com/harriswang/gsm-governance/discussions](https://github.com/harriswang/gsm-governance/discussions)

---

<p align="center">
  <em>Built with a commitment to analytical rigour, normative transparency, and empirical honesty.</em>
</p>
