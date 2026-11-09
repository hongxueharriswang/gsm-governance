# gsm-governance

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.4.0-green.svg)](https://github.com/hongxueharriswang/gsm-governance/releases/tag/v0.4.0)
[![Status](https://img.shields.io/badge/status-research%20software-orange.svg)]()

Reference implementation of the **computational theory of justice-centered
multi-level governance** (GSM-J).

> Wang, H. *A Computational Theory of Justice-Centered Multi-Level Governance
> for Human Flourishing under Bounded Non-Exploitation.* Preprint, 2026.

This library implements the **v5** version of the theory. It is not a
simulation toy, not a normative essay with code attached, and not a general
governance package. It is the reference implementation of a specific
computational theory whose normative parameters are explicit, swappable, and
reported — the property the paper calls *conditional normative status*
(§1.7).

---

## Citation

If you use this library, please cite both the paper and the software:

```bibtex
@article{wang2026gsmj,
  author  = {Wang, Harris},
  title   = {A Computational Theory of Justice-Centered Multi-Level Governance
             for Human Flourishing under Bounded Non-Exploitation},
  year    = {2026},
  note    = {Preprint}
}

@software{wang2026gsmgovernance,
  author  = {Wang, Harris},
  title   = {gsm-governance: Reference implementation of the computational
             theory of justice-centered multi-level governance},
  version = {0.4.0},
  year    = {2026},
  url     = {https://github.com/hongxueharriswang/gsm-governance},
  license = {MIT}
}
```

---

## What this library does

The theory on which this library is based has an **irreducible core** of three
innovations (§1.4). Every other element in the library exists to make those
three things precise, testable, and usable.

| Core innovation | Implementation |
|---|---|
| **The justice gap** — bounded non-exploitation is necessary but insufficient for justice | `constraints.py` separates C1 (non-exploitation) from C2–C4 (floors, vulnerability, alignment), so satisfying one does not satisfy the others |
| **The five-dimensional justice capability** | `entities.State.justice` is a five-entry dict; `welfare.WelfareEvaluator` applies dimension-specific weights |
| **The justice-centered constraint architecture** | C1–C4 enforced independently in `constraints.py`; C4 is dimension-specific and absolute, not aggregate and proportional |

Beyond the core, the library implements:

- **Decomposed interaction matrix** `M_J = M_J⁺ + M_J⁻` with contested vs.
  single-component pair typing (§3.3.2)
- **Vertical alignment pressure** in the justice dynamics — the `β_d(J_parent − J)`
  term of §4.1
- **Dimension-specific accountability** (§3.7)
- **Multi-channel policy intervention** with cost, horizon, and recovery (§4.1)
- **Quadratic prioritarian welfare** as the default (§4.3)
- **Estimation scaffold** for `M_J` with sign priors and component mask (Appendix D)

---

## What this library does *not* do

Two things are deliberately absent, and their absence is stated in the code
itself rather than papered over:

### 1. It does not estimate `M_J` from panel data

`gsm_governance.estimation.estimate_MJ` raises `NotImplementedError` with a
message explaining why. The paper (§3.3.3, Appendix D.7) is explicit that
component identification requires natural experiments or cross-context
designs that a library cannot manufacture. The scaffold supplies the data
structures — `EstimationSpec` with sign priors and component mask — that a
downstream Bayesian implementation would need, and nothing more.

### 2. It does not wire the empirical roadmap of §6.3

`gsm_governance.data` supplies **illustrative profiles** from the paper's
stylized-Nordic demonstration. These are not measurements of any country. The
paper names OECD *How's Life?*, V-Dem, World Justice Project, World Values
Survey, SDG, and IMF as candidate sources for calibration. Wiring those
sources into a four-level panel is downstream empirical work, not a library
feature.

Everything else is implemented and tested. If you want the library to do one
of these two things, open an issue — both are marked for future work in the
roadmap below.

---

## Installation

### From source (current)

```bash
git clone https://github.com/hongxueharriswang/gsm-governance.git
cd gsm-governance
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Unix / macOS:
source .venv/bin/activate

pip install -e ".[dev]"
```

The library requires **Python 3.9+**. The core has no mandatory dependencies;
`pytest` and `numpy` are available as the `dev` extra.

### From PyPI

Not yet published. Track issue #1 if you want it.

---

## Quick start

```python
from gsm_governance import GSMConfig, Simulation, load_stylized_nordic

config = GSMConfig(seed=42)
jurisdictions = load_stylized_nordic()
sim = Simulation(config, jurisdictions)
history = sim.run(n_steps=20)

final = history[-1]["welfare"]
print(f"welfare       = {final['total']:.4f}")
print(f"  base        = {final['base']:.4f}")
print(f"  exploitation= {final['exploitation_penalty']:.4f}")
print(f"C2 violations = {len(history[-1]['violations']['c2'])}")
```

Output (stylized-Nordic illustrative profiles, default configuration):

```
welfare       = 3.7521
  base        = 3.7521
  exploitation= 0.0000
C2 violations = 9
```

The C2 violations are the point: the paper's §6.1 finding is that aggregate
welfare can improve while recognition, corrective, and intergenerational
floors remain violated. The library is designed to make that visible.

See `examples/stylized_nordic.py` for a full 20-step trace.

---

## Core concepts

A short orientation to the objects the library exposes. For the full
theoretical account, see the paper.

### The state vector

Each jurisdiction carries a six-dimensional state:

```python
State(
    capabilities={
        "accountability": 0.85,
        "competence":     0.80,
        "cohesion":       0.82,
        "continuity":     0.78,
        "learning":       0.80,
    },
    justice={
        "distributive":     0.78,
        "procedural":       0.80,
        "recognition":      0.62,
        "corrective":       0.45,
        "intergenerational":0.55,
    },
)
```

The five justice dimensions are **irreducible** (§3.3.1). Aggregation exists
for reporting and welfare; the constraints and accountability rules operate on
the disaggregated vector. The library enforces this by never aggregating
inside a constraint check.

### The interaction matrix

The matrix decomposes into two components (§3.3.2):

```python
from gsm_governance import JusticeInteractionMatrix

M = JusticeInteractionMatrix()

# The net coefficient, for reporting:
M.m[("intergenerational", "procedural")]        # -0.05 + 0.10 = 0.05

# The components, for interpretation:
M.m_plus[("intergenerational", "procedural")]   # 0.10  (synergy)
M.m_minus[("intergenerational", "procedural")]  # -0.05 (tension)

# Pair typing:
M.pair_type("intergenerational", "procedural")  # "contested"
M.pair_type("procedural", "intergenerational")  # "single_component_tension"
M.pair_type("distributive", "recognition")      # "uncommitted"
```

A **contested pair** carries both components. A net near zero for a contested
pair is uninformative — it may reflect two large offsetting mechanisms. A net
near zero for a **single-component pair** is evidence against the proposed
mechanism. This distinction is the formal content of hypothesis H6.

### The four constraints

| Constraint | Meaning | Function |
|---|---|---|
| **C1** | Bounded non-exploitation: `E_ij ≤ τ_j` or `Comp_ij ≥ E_ij` | `check_c1(...)` |
| **C2** | Dimension-specific floor: `J^d ≥ J_min^d` | `check_c2(...)` |
| **C3** | Vulnerability-sensitive threshold: `τ_j^vuln = φ_vuln · τ_j` when `J̄ < J_min^agg` | `check_c3(...)` (reports vulnerable ids) + `effective_tau(...)` |
| **C4** | Absolute vertical alignment: `J_child^d ≥ J_parent^d − φ_d` | `check_c4(...)` |

**C3 is not zero tolerance.** It reduces the threshold; it does not forbid all
exploitation of a vulnerable party. Use `effective_tau(jurisdiction, config)`
to get the correct threshold for C1.

**C4 is absolute, not proportional.** A child may fall below a high-performing
parent by at most `φ_d`, not by a fraction of the parent's score. This is what
prevents a high-distributive parent from masking a low-recognition child.

```python
from gsm_governance import (
    GSMConfig, load_stylized_nordic,
    check_c1, check_c2, check_c3, check_c4, check_all,
)

config = GSMConfig()
juris  = load_stylized_nordic()

exploitation = {("national", "province"): 0.08}
compensation = {}  # nothing offered

check_c1(juris, exploitation, compensation, config)  # [("national", "province")]
check_c2(juris, config)                               # floors below threshold
check_c3(juris, config)                               # vulnerable jurisdiction ids
check_c4(juris, config)                               # alignment shortfalls
```

### The welfare function

Two forms are supported:

```python
# §4.3 default — quadratic shortfall from 1:
#   W = Σ w_d [γ_d J − δ_d (1 − J)²]
WelfareEvaluator(GSMConfig(welfare_mode="quadratic"))

# linear floor penalty (0.3.0 behaviour), for comparison:
#   W = Σ w_d γ_d J − Σ w_d δ_d max(0, J_min − J)
WelfareEvaluator(GSMConfig(welfare_mode="linear_floor"))
```

Prioritarian condition is `δ_d > γ_d` in every dimension:

```python
config = GSMConfig(
    gamma_w={d: 0.20 for d in ["distributive","procedural","recognition",
                               "corrective","intergenerational"]},
    delta_w={d: 1.00 for d in ["distributive","procedural","recognition",
                               "corrective","intergenerational"]},
)
WelfareEvaluator(config).is_prioritarian()   # True
```

---

## Module reference

| Module | Responsibility | Paper reference |
|---|---|---|
| `config` | `GSMConfig` — every normative parameter as an explicit field | §7.2 |
| `entities` | `State`, `Jurisdiction` — the state vector and level hierarchy | §3.1, §3.2 |
| `justice` | `JusticeInteractionMatrix` — decomposed `M_J` with pair typing | §3.3.2 |
| `dynamics` | `justice_step`, `capability_step` — the update rules | §4.1, §4.2 |
| `constraints` | `check_c1`…`check_c4`, `effective_tau` | §3.6 |
| `compensation` | `CompensationVector` — the six-channel compensation schema | §3.5, Table 7 |
| `welfare` | `WelfareEvaluator` — quadratic and linear modes | §4.3 |
| `accountability` | `Accountability` — dimension-specific cross-level penalties | §3.7 |
| `enforcement` | `PolicyInterventionEnforcer`, `Intervention` | §4.1 |
| `simulation` | `Simulation` — the end-to-end engine | §3–§4 |
| `estimation` | `EstimationSpec`, `estimate_MJ` (scaffold) | §3.3.3, App. D |
| `data` | `load_stylized_nordic()` — illustrative profiles | §6 |

---

## Walkthrough: policy intervention

The paper's §4.1 models intervention as a costly, multi-channel operation
with a finite horizon. Here is a worked example:

```python
from gsm_governance import (
    GSMConfig, Simulation, Intervention, load_stylized_nordic,
)

config = GSMConfig(seed=42)
juris  = load_stylized_nordic()
sim    = Simulation(config, juris)

# Intervention: fiscal transfer to the province, t=2 to t=7
sim.enforcer.add(Intervention(
    jurisdiction_id="province",
    start_t=2,
    channel="fiscal",
    magnitude=0.30,
    authority="national",
))

history = sim.run(n_steps=20)

# The intervention cost shows up in cohesion and continuity
for t in (0, 5, 15):
    row = history[t]
    print(f"t={t:>2}  justice(D)=...  violations_c2={len(row['violations']['c2'])}")

# The endogenous frequency ceiling (H7) is predicted from κ_int:
print(f"predicted ceiling: {sim.enforcer.predicted_frequency_ceiling():.2f} "
      f"interventions per period")
```

Available channels: `fiscal`, `infrastructural`, `representational`,
`regulatory`, `future`, `restitutional`. Each targets a different dimension
combination — see `enforcement.py` for the table.

---

## Configuration

`GSMConfig` exposes every normative parameter the paper lists in §7.2. All
parameters are settable; changing any of them produces a different model whose
consequences are inspectable. That is what conditional normative status means
in code.

| Group | Parameter | Default | Paper reference |
|---|---|---|---|
| Dynamics | `alpha[d]` | 0.10 | §4.1 |
| | `beta[d]` | 0.08 | §4.1 (alignment pressure) |
| | `gamma[d]` | 0.05 | §4.1 (exploitation drag) |
| Welfare | `gamma_w[d]` | 1.00 | §4.3 |
| | `delta_w[d]` | 0.50 | §4.3 (prioritarian if > γ_w) |
| | `weights[d]` | 0.20 (uniform) | §3.3 |
| | `welfare_mode` | `"quadratic"` | §4.3 |
| Floors | `floors[d]` | per Table 8 | §3.6.2 |
| | `aggregate_floor` | 0.22 | §3.6.3 (C3 trigger) |
| | `default_tau` | 0.05 | §3.6.1 |
| Constraints | `phi_vuln` | 0.50 | §3.6.3 (C3) |
| | `phi_d[d]` | 0.05 | §3.6.4 (C4) |
| | `lambda_pd[d]` | 0.05 | §3.7 |
| Interaction | `m_max` | 0.30 | §3.3.2 |
| | `symmetry` | `"asymmetric"` | §3.3.3 |
| Intervention | `kappa_int` | 0.10 | §4.1 |
| | `tau_int` | 5 | §4.1 |
| | `omega_k[channel]` | per channel | §4.1 |
| | `recovery_rate` | 0.02 | §4.1 |

Defaults are illustrative placeholders, not substantive recommendations. The
paper's §3.6.2 states this explicitly for floors; it applies to the whole
table.

---

## Versioning and migration

This library follows the theory's version history.

| Library | Theory version | Notes |
|---|---|---|
| 0.4.0 (current) | v5 preprint | Decomposed `M_J`, corrected C3 and C4, quadratic welfare, alignment pressure |
| 0.3.0 | v3 preprint | Single signed `M_J`, zero-tolerance C3, proportional C4, linear floor welfare |

### Migrating from 0.3.0

Four changes will affect existing code. Each is a *behaviour* change, not just
an API change.

**1. `GSMConfig.phi` is split into `phi_vuln` and `phi_d`.**

```python
# 0.3.0
config = GSMConfig(phi=0.50)

# 0.4.0
config = GSMConfig(phi_vuln=0.50, phi_d={d: 0.05 for d in DIMENSIONS})
```

**2. C3 is a reduced threshold, not zero tolerance.**

Under 0.3.0, any exploitation of a vulnerable jurisdiction was a C1 violation.
Under 0.4.0, exploitation up to `phi_vuln * tau` is permitted. If you depended
on the strict behaviour, set `phi_vuln = 0.0`.

**3. C4 is an absolute margin, not a proportional one.**

Under 0.3.0, `J_child ≥ phi * J_parent`. Under 0.4.0, `J_child ≥ J_parent − phi_d`.
To approximate the old behaviour, set `phi_d[d]` to `(1 − phi) * typical_parent_justice[d]`.

**4. Welfare defaults to quadratic.**

`WelfareEvaluator(config).welfare(juris)` now returns the §4.3 quadratic form.
For 0.3.0's linear floor penalty, pass `welfare_mode="linear_floor"` when
constructing `GSMConfig`.

**Backward-compatible:** `JusticeInteractionMatrix.m` remains readable as a
property returning `m_plus + m_minus`. `load_denmark_raw()` is retained as a
deprecated alias for `load_stylized_nordic_raw()`.

---

## Development

### Environment

```bash
git clone https://github.com/hongxueharriswang/gsm-governance.git
cd gsm-governance
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### VS Code

The repository ships with `.vscode/settings.json`, `launch.json`, and
`extensions.json`. Open the folder in VS Code and accept the recommended
extensions (Python, Pylance). Test discovery and debug configurations for both
the example script and the full test suite are pre-configured.

### Testing

```bash
pytest                    # all tests
pytest -v                 # verbose
pytest tests/test_gsm.py::test_c3_uses_reduced_threshold_not_zero  # one test
```

The suite covers the four constraint behaviours, the `M_J` decomposition,
welfare modes, the alignment-pressure term, compensation adequacy, intervention
cost effects, and end-to-end simulation.

### Running the example

```bash
python examples/stylized_nordic.py
```

Prints a 20-step trace of welfare, base welfare, exploitation penalties, and
C1–C4 violation counts, then final justice by jurisdiction.

---

## Contributing

Issues and pull requests are welcome. Two ground rules for this repository:

**Keep the paper and the library in sync.** If you change a function that
implements a numbered paper claim, update the docstring's section reference and
add or amend a test. The tests are organized by paper section for this reason.

**Do not overclaim.** The library's honesty about what it does not do is a
feature. A pull request that turns `estimate_MJ` from an explicit
`NotImplementedError` into an approximation without stating the identification
problem it does not solve will be rejected. A pull request that implements
estimation *and* documents what identification assumption it imposes will be
considered carefully.

### Reporting bugs

Include:

- Python version (`python --version`)
- Library version (`python -c "import gsm_governance; print(gsm_governance.__version__)"`)
- Minimal reproducible example
- For constraint-related bugs: the `GSMConfig` values and the `State` that triggered the failure

---

## Roadmap

Open items, in rough priority order. Each maps to a paper section.

| Item | Target | Paper reference |
|---|---|---|
| Wire OECD / V-Dem / WJP / WVS into a four-level panel loader | v0.5.0 | §6.3 |
| Implement `estimate_MJ` with sign priors and cross-context identification | v0.5.0 | §3.3.3, App. D |
| Add a reporting module that produces the Appendix B checklist | v0.5.0 | App. B |
| Sensitivity analysis harness (sweep all `GSMConfig` parameters) | v0.5.0 | §1.7 |
| Publish to PyPI | v0.5.0 | — |
| Add a `M_J` visualizer (matrix as component-signed heatmap) | v0.6.0 | §3.3.2 |
| Reference implementation of the model constitution | separate repo | — |

---

## Related work

The library draws on six traditions named in the paper (§1.3): systems theory,
polycentric governance, institutional economics, capability theory, eudaimonic
well-being, and contemporary justice theory. The interaction-matrix
decomposition is closest in spirit to signed-network models in institutional
analysis; the constraint architecture is closest to sufficientarian capability
thresholds.

A **model constitutional instrument** derived from this theory — *The
Justice-Centered Multi-Level Governance Constitution* — is in preparation as a
separate deliverable. It translates the library's constraints (C1–C4), pair
typing, and parameterization into enforceable constitutional language. It is
not in this repository.

---

## License

MIT. See [`LICENSE`](LICENSE).

---

## Acknowledgments

The theory's conditional normative status is not a rhetorical hedge; it is a
design commitment. The library's most useful property may be that it makes the
commitment auditable: every normative parameter is in `GSMConfig`, every
constraint is in `constraints.py`, and every claim about identification is
stated where the code would otherwise overclaim. Thanks to the reviewers whose
comments on the paper prompted the changes that produced 0.4.0.
