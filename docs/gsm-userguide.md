# `gsm-governance` User Guide

**Version 0.4.0 — complete API reference with worked examples**

---

## About this guide

This is the reference document for `gsm-governance`. It documents every public class and function, states what each returns, gives a runnable example for each, and notes the edge cases that matter in practice.

Three other documents accompany this one:

- **`README.md`** — overview, installation, and what the library does and does not do. Read this first.
- **`TUTORIAL.md`** — research workflows (diagnostics, intervention experiments, sensitivity analysis, custom models). Read this second.
- **The paper** — the theory itself. §1.4 for the irreducible core, §3.3.2 for the interaction decomposition, §3.6 for constraints, §4.3 for welfare. Read this alongside the guide when a design decision is unclear.

This guide is the *third* stop. It assumes you know what you want to do and need to know how to call the function that does it.

**Sections 4 through 15 document the modules.** Section 16 is a cookbook of common recipes. Sections 17–19 cover errors, performance, and extension. Section 20 is an API index.

**Two honest notes up front.**

First, `check_c1` as delivered uses `jurisdiction.tau` directly, not the vulnerability-adjusted threshold `effective_tau(...)`. Section 8.1 documents this and supplies the corrected variant. Use the corrected variant in research code.

Second, `estimate_MJ` is a documented scaffold, not a working estimator. Section 14 explains what it is for.

---

## 1. Installation and verification

```bash
git clone https://github.com/hongxueharriswang/gsm-governance.git
cd gsm-governance
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest                             # 13 tests should pass
python examples/stylized_nordic.py # runs in ~1s
```

**Verify the version.**

```python
import gsm_governance
assert gsm_governance.__version__ == "0.4.0"
```

The library is versioned to the paper. `0.4.0` implements v5 of the theory. `0.3.0` implements v3 and is not interchangeable: C3, C4, welfare form, and the dynamics all changed. If you are working from a paper draft older than v5, check which library version corresponds to it.

**Minimum Python version.** 3.9. The library uses `dataclasses`, `frozenset`, and typed `dict[...]` annotations, and nothing newer.

**Dependencies.** None for the core library. `pytest` and `numpy` are the `dev` extra, used by the test suite only. The estimation scaffold exposes data structures but does not import numpy.

---

## 2. Concepts primer

Three sentences, for orientation. The paper has the full account.

The **state** of a jurisdiction is six capabilities `[A, C, S, T, L, J]` where `J` is a five-dimensional justice vector `[distributive, procedural, recognition, corrective, intergenerational]` (§3.2).

The **interaction matrix** `M_J = M_J⁺ + M_J⁻` captures cross-dimension effects, and is **decomposed** so that a contested pair — carrying both synergy and tension components — can be distinguished from a single-component pair (§3.3.2).

The **four constraints** C1–C4 (§3.6) ensure that non-exploitation is bounded, that no dimension falls below its floor, that vulnerability reduces the exploitation threshold, and that a child jurisdiction cannot fall below its parent by more than a fixed margin per dimension.

Everything else in the library supports these three things.

---

## 3. Quick start

If you want to run something immediately:

```python
from gsm_governance import GSMConfig, Simulation, load_stylized_nordic

config = GSMConfig(seed=42)
jurisdictions = load_stylized_nordic()
sim = Simulation(config, jurisdictions)
history = sim.run(n_steps=20)

final = history[-1]
print(f"welfare       = {final['welfare']['total']:.4f}")
print(f"C2 violations = {len(final['violations']['c2'])}")
print(f"C4 violations = {len(final['violations']['c4'])}")
```

Expected output (default config, stylized-Nordic profiles):

```
welfare       = 3.7521
C2 violations = 9
C4 violations = 12
```

The C2 and C4 counts are the finding, not a bug. §6.1 of the paper claims aggregate welfare can improve while dimension floors remain violated. The library reproduces that claim.

Everything below documents the pieces that produce this output.

---

## 4. `gsm_governance.entities`

Two dataclasses. `State` holds the six-dimensional state vector. `Jurisdiction` holds a `State`, its level, its parent, and its children.

### 4.1 `State`

**Signature.**

```python
@dataclass
class State:
    capabilities: Dict[str, float]  # keys: accountability, competence, cohesion, continuity, learning
    justice:      Dict[str, float]  # keys: distributive, procedural, recognition, corrective, intergenerational
```

**Defaults.** All values `0.5`.

**Example.**

```python
from gsm_governance import State

s = State(
    capabilities={"accountability": 0.85, "competence": 0.80,
                  "cohesion": 0.82, "continuity": 0.78, "learning": 0.80},
    justice={"distributive": 0.78, "procedural": 0.80, "recognition": 0.62,
             "corrective": 0.45, "intergenerational": 0.55},
)
print(s.aggregate_justice({"distributive": 0.2, "procedural": 0.2,
                           "recognition": 0.2, "corrective": 0.2,
                           "intergenerational": 0.2}))
```

**Methods.**

- `aggregate_justice(weights)` — returns `Σ w_d · J_d`. Use for reporting only; constraints never call this (§3.3.1).
- `clip()` — clamps all values to `[0, 1]`. Called automatically by `Simulation.step()`.
- `copy()` — returns a deep copy. Useful when you need to snapshot state before an update.

**Notes.** Missing keys are not filled in. If you construct a `State` with only some dimensions populated, downstream code will `KeyError`. Always populate all five of `DIMENSIONS` and all five of `CAPABILITIES`. The defaults give you `0.5` everywhere, which is a safe neutral starting point.

### 4.2 `Jurisdiction`

**Signature.**

```python
@dataclass
class Jurisdiction:
    id:      str
    level:   int
    state:   State           = State()
    parent:  Jurisdiction    = None
    children: List[Jurisdiction] = []
    tau:     float           = 0.05
```

**Example.**

```python
from gsm_governance import Jurisdiction, State

national = Jurisdiction(id="national", level=1, tau=0.05)
province = Jurisdiction(id="province", level=2, tau=0.05)
national.add_child(province)

assert province.parent is national
assert province in national.children
```

**Methods.**

- `add_child(child)` — sets `child.parent = self` and appends to `self.children`. The library does not prevent cycles or duplicate ids. Check your own data.

**Notes.** `level` is descriptive, not enforced. The library does not verify that a `level=1` jurisdiction has no parent or that a `level=2` has one. Parent-child relationships are the only structural constraint the simulation reads.

### 4.3 Constants

`DIMENSIONS` and `CAPABILITIES` are tuples exported from `gsm_governance`:

```python
from gsm_governance import DIMENSIONS, CAPABILITIES

print(DIMENSIONS)   # ('distributive', 'procedural', 'recognition', 'corrective', 'intergenerational')
print(CAPABILITIES) # ('accountability', 'competence', 'cohesion', 'continuity', 'learning')
```

Use these rather than hardcoding strings. They are the keys for every dict in the library.

---

## 5. `gsm_governance.config.GSMConfig`

The single object that holds every normative parameter. §7.2 of the paper lists what must be reported; `GSMConfig` makes it possible to record all of it.

### 5.1 Fields

Fields are grouped by paper section. Every field is a mutable attribute; use `dataclasses.replace()` to derive variants (validation runs automatically).

| Group | Field | Type | Default | §|
|---|---|---|---|---|
| Dynamics | `alpha` | `dict[str, float]` | `0.10` all | 4.1 |
| | `beta` | `dict[str, float]` | `0.08` all | 4.1 |
| | `gamma` | `dict[str, float]` | `0.05` all | 4.1 |
| Welfare | `gamma_w` | `dict[str, float]` | `1.00` all | 4.3 |
| | `delta_w` | `dict[str, float]` | `0.50` all | 4.3 |
| | `weights` | `dict[str, float]` | `0.20` all | 3.3 |
| | `welfare_mode` | `str` | `"quadratic"` | 4.3 |
| Floors | `floors` | `dict[str, float]` | per Table 8 | 3.6.2 |
| | `aggregate_floor` | `float` | `0.22` | 3.6.3 |
| | `default_tau` | `float` | `0.05` | 3.6.1 |
| Constraints | `phi_vuln` | `float` | `0.50` | 3.6.3 |
| | `phi_d` | `dict[str, float]` | `0.05` all | 3.6.4 |
| | `lambda_pd` | `dict[str, float]` | `0.05` all | 3.7 |
| Interaction | `m_max` | `float` | `0.30` | 3.3.2 |
| | `symmetry` | `str` | `"asymmetric"` | 3.3.3 |
| Coupling | `capability_coupling` | `dict[str, float]` | `0.02` all | 4.2 |
| Intervention | `kappa_int` | `float` | `0.10` | 4.1 |
| | `tau_int` | `int` | `5` | 4.1 |
| | `omega_k` | `dict[str, float]` | per channel | 4.1 |
| | `recovery_rate` | `float` | `0.02` | 4.1 |
| Numerics | `epsilon` | `float` | `1e-9` | — |
| | `seed` | `int \| None` | `None` | — |

### 5.2 Validation

`__post_init__` raises `ValueError` on:

- `weights` not summing to `1.0` (tolerance `1e-6`)
- Any `phi_d[d] < 0`
- Any `gamma_w[d] <= 0`
- Any `delta_w[d] < 0`
- `phi_vuln` not in `[0, 1]`
- `welfare_mode` not in `{"quadratic", "linear_floor"}`
- `symmetry` not in `{"symmetric", "asymmetric"}`

Invalid configurations fail loudly rather than silently producing wrong results.

### 5.3 Example: a prioritarian configuration

The default is **not** prioritarian (`delta_w = 0.50 < gamma_w = 1.00`). To make it prioritarian, raise `delta_w` above `gamma_w`:

```python
from gsm_governance import GSMConfig, DIMENSIONS
from gsm_governance.welfare import WelfareEvaluator

config = GSMConfig(
    gamma_w={d: 0.20 for d in DIMENSIONS},
    delta_w={d: 1.00 for d in DIMENSIONS},
)
assert WelfareEvaluator(config).is_prioritarian()
```

### 5.4 Example: deriving a variant

```python
from dataclasses import replace
from gsm_governance import GSMConfig

baseline = GSMConfig(seed=42)
strict = replace(baseline, phi_vuln=0.0)   # zero-tolerance vulnerability (0.3.0 behaviour)
```

### 5.5 Reporting

Serialize with `dataclasses.asdict`. Report every field, including defaults.

```python
import json
from dataclasses import asdict

with open("config.json", "w") as f:
    json.dump(asdict(GSMConfig(seed=42)), f, indent=2)
```

---

## 6. `gsm_governance.justice.JusticeInteractionMatrix`

The decomposed interaction matrix. The paper's §3.3.2 is the reference; the class implements `M_J = M_J⁺ + M_J⁻` with component bounds and pair typing.

### 6.1 Construction

**Signature.**

```python
@dataclass
class JusticeInteractionMatrix:
    m_max:    float                       = 0.30
    symmetry: str                         = "asymmetric"
    m_plus:   Dict[Tuple[str, str], float] = <default priors>
    m_minus:  Dict[Tuple[str, str], float] = <default priors>
```

**Example.**

```python
from gsm_governance import JusticeInteractionMatrix

# Defaults (illustrative priors from §3.3.2, Tables 4 and 5)
M = JusticeInteractionMatrix()

# Custom matrix (all coefficients supplied by you)
M = JusticeInteractionMatrix(
    m_max=0.30,
    m_plus={
        ("procedural", "recognition"): 0.10,
        ("intergenerational", "procedural"): 0.08,  # contested: synergy part
    },
    m_minus={
        ("intergenerational", "distributive"): -0.05,
        ("intergenerational", "procedural"): -0.04,  # contested: tension part
    },
)
```

**Validation.** `__post_init__` raises `ValueError` if:

- Any key is not a pair of `DIMENSIONS`
- Any `m_plus` value is outside `[0, m_max]`
- Any `m_minus` value is outside `[-m_max, 0]`
- Any net exceeds `|m_max|`

**Symmetrization.** With `symmetry="symmetric"`, each unordered pair is averaged:

```python
M = JusticeInteractionMatrix(
    symmetry="symmetric",
    m_plus={("procedural", "recognition"): 0.10},   # only one direction
)
print(M.m_plus[("recognition", "procedural")])      # 0.05 (averaged)
```

### 6.2 Pair typing

§3.3.2 of the paper distinguishes one **contested pair** `(I, P)` from eleven **single-component pairs**.

```python
from gsm_governance import (
    JusticeInteractionMatrix,
    CONTESTED_PAIRS,
    SINGLE_COMPONENT_TENSION_PAIRS,
    SINGLE_COMPONENT_SYNERGY_PAIRS,
)

M = JusticeInteractionMatrix()

M.pair_type("intergenerational", "procedural")    # "contested"
M.pair_type("procedural", "intergenerational")    # "single_component_tension"
M.pair_type("procedural", "recognition")          # "single_component_synergy"
M.pair_type("distributive", "recognition")        # "uncommitted"
M.pair_type("recognition", "distributive")        # "uncommitted"
```

**Why the typing matters.** For a contested pair, a net near zero is uninformative — two large components may be cancelling. For a single-component pair, a net near zero is evidence against the proposed mechanism. H6 in the paper is a hypothesis about this difference.

Verify the counts:

```python
assert len(CONTESTED_PAIRS) == 1
assert len(SINGLE_COMPONENT_TENSION_PAIRS) == 4
assert len(SINGLE_COMPONENT_SYNERGY_PAIRS) == 7
assert len(CONTESTED_PAIRS | SINGLE_COMPONENT_TENSION_PAIRS | SINGLE_COMPONENT_SYNERGY_PAIRS) == 12
```

### 6.3 Accessing coefficients

**`m` (property).** Net coefficients, `m_plus + m_minus`. Read-only; returns a fresh dict on each access.

```python
M = JusticeInteractionMatrix()
net = M.m[("intergenerational", "procedural")]
assert abs(net - 0.05) < 1e-9  # +0.10 - 0.05
```

**`get(d, e)`.** Single net coefficient with `0.0` default.

```python
M.get("distributive", "procedural")   # 0.06
M.get("distributive", "recognition")  # 0.0 (uncommitted pair)
```

### 6.4 Coupling

`coupling(justice)` returns `C_J^d(J_i)` for each dimension (§3.3.2):

```python
M = JusticeInteractionMatrix()
J = {"distributive": 0.60, "procedural": 0.60, "recognition": 0.60,
     "corrective": 0.60, "intergenerational": 0.60}

C = M.coupling(J)
# C["distributive"] = sum_{e != D} (m_+[D,e] + m_-[D,e]) * J[e] * (1 - J[D])
```

The `(1 - J_i^d)` factor imposes diminishing returns: as a dimension approaches 1, its coupling effect shrinks.

---

## 7. `gsm_governance.dynamics`

Two functions implementing the update rules of §4.1 and §4.2.

### 7.1 `justice_step`

**Signature.**

```python
def justice_step(
    jurisdiction: Jurisdiction,
    config: GSMConfig,
    interaction: JusticeInteractionMatrix,
    exploitation_by_dim: Optional[dict] = None,
) -> dict:
```

Returns a dict of **increments** `dJ[d]`, not new values. The caller adds them to `jurisdiction.state.justice` and clips.

**Formula (§4.1).**

```
dJ[d] = α_d · ( C_J^d(J) + β_d·(J_parent[d] − J[d]) − γ_d·E[d] )
```

The three terms are: endogenous interaction, vertical alignment pressure, exploitation drag.

**Example.**

```python
from gsm_governance import (
    GSMConfig, State, Jurisdiction, JusticeInteractionMatrix, DIMENSIONS,
)
from gsm_governance.dynamics import justice_step

config = GSMConfig()
M = JusticeInteractionMatrix()

parent = Jurisdiction(id="p", level=1,
                      state=State(justice={d: 0.80 for d in DIMENSIONS}))
child = Jurisdiction(id="c", level=2,
                     state=State(justice={d: 0.40 for d in DIMENSIONS}))
parent.add_child(child)

dJ = justice_step(child, config, M)
print(f"dJ['distributive'] = {dJ['distributive']:.6f}")

for d in DIMENSIONS:
    child.state.justice[d] += dJ[d]
child.state.clip()
```

**Notes.** `beta` matters. With default `β = 0.08` and parent at `0.80` while child is at `0.40`, the alignment term alone is `0.08 × 0.40 = 0.032` — larger than the interaction and drag terms combined at these values. If you want C4 to be enforced only as a post-hoc constraint, not as a force, set `β = 0`.

### 7.2 `capability_step`

**Signature.**

```python
def capability_step(
    jurisdiction: Jurisdiction,
    config: GSMConfig,
    deltas: Optional[dict] = None,
) -> dict:
```

Returns increments `dC[c]`. The formula is a first-order drift toward mean justice, modulated by `capability_coupling`:

```
dC[c] = coupling[c]·(mean(J) − C[c]) + deltas[c]
```

**Example.**

```python
from gsm_governance.dynamics import capability_step

dC = capability_step(child, config)
for c, dv in dC.items():
    child.state.capabilities[c] += dv
child.state.clip()
```

**Notes.** §4.2 of the paper commits to co-evolution as a theoretical property but does not fix the form. The library's drift-toward-mean is a placeholder, not a substantive claim. Override it if your research question requires a specific coupling.

---

## 8. `gsm_governance.constraints`

Four constraint checks. Use `check_all` for a summary, or the individual functions for fine-grained diagnostics.

### 8.1 `check_c1` — bounded non-exploitation

**Signature.**

```python
def check_c1(
    jurisdictions: List[Jurisdiction],
    exploitation: Dict[Tuple[str, str], float],
    compensation: Dict[Tuple[str, str], CompensationVector],
    config: GSMConfig,
) -> List[Tuple[str, str]]:
```

**What it checks.** For each `(i, j)` with `E_ij > 0`, a violation occurs when `E_ij > tau_j` **and** compensation is not adequate. `tau_j` here is `jurisdictions[j].tau` **directly**, not the vulnerability-adjusted threshold.

**⚠ Important.** This is the behavior of `check_c1` as delivered. Per §3.6.3 of the paper, C1 must use `effective_tau(...)` — the vulnerability-reduced threshold. To honor the paper, override:

```python
from gsm_governance.constraints import effective_tau
from gsm_governance import check_c1

def check_c1_corrected(jurisdictions, exploitation, compensation, config):
    """C1 with §3.6.3 vulnerability adjustment."""
    by_id = {j.id: j for j in jurisdictions}
    violations = []
    for (i, j), e in exploitation.items():
        if e <= 0.0:
            continue
        tau_eff = effective_tau(by_id[j], config) if j in by_id else config.default_tau
        if e <= tau_eff + config.epsilon:
            continue
        comp = compensation.get((i, j))
        if comp is None or not comp.is_adequate(e, config):
            violations.append((i, j))
    return violations
```

Report the substitution in your paper's methods.

**Example.**

```python
from gsm_governance import GSMConfig, Jurisdiction, State, check_c1, DIMENSIONS
from gsm_governance.compensation import CompensationVector

config = GSMConfig()
parent = Jurisdiction(id="p", level=1, tau=0.10)
child = Jurisdiction(id="c", level=2, tau=0.10,
                     state=State(justice={d: 0.80 for d in DIMENSIONS}))

# Exploitation above threshold, no compensation → violation
expl = {("p", "c"): 0.15}
assert check_c1([parent, child], expl, {}, config) == [("p", "c")]

# Same exploitation, adequate compensation → no violation
comp = {("p", "c"): CompensationVector(fiscal=0.20)}
assert check_c1([parent, child], expl, comp, config) == []
```

### 8.2 `check_c2` — dimension floors

**Signature.**

```python
def check_c2(
    jurisdictions: List[Jurisdiction],
    config: GSMConfig,
) -> List[Tuple[str, str, float]]:
```

**What it checks.** For each jurisdiction and each dimension, a violation occurs when `J^d < J_min^d`. Returns `(jurisdiction_id, dimension, actual_value)`.

**Example.**

```python
from gsm_governance import GSMConfig, Jurisdiction, State, check_c2, DIMENSIONS

config = GSMConfig(floors={d: 0.50 for d in DIMENSIONS})
j = Jurisdiction(id="j", level=1,
                 state=State(justice={"distributive": 0.40, "procedural": 0.60,
                                      "recognition": 0.30, "corrective": 0.20,
                                      "intergenerational": 0.55}))
violations = check_c2([j], config)
# [('j', 'distributive', 0.4), ('j', 'recognition', 0.3),
#  ('j', 'corrective', 0.2)]
```

### 8.3 `effective_tau` and `check_c3` — vulnerability sensitivity

**`effective_tau` signature.**

```python
def effective_tau(jurisdiction: Jurisdiction, config: GSMConfig) -> float:
```

Returns `phi_vuln · tau` if aggregate justice is below `aggregate_floor`, else `tau`.

**`check_c3` signature.**

```python
def check_c3(jurisdictions: List[Jurisdiction], config: GSMConfig) -> List[str]:
```

Returns the ids of jurisdictions currently subject to a reduced threshold.

**Example.**

```python
from gsm_governance import GSMConfig, Jurisdiction, State, check_c3, DIMENSIONS
from gsm_governance.constraints import effective_tau

config = GSMConfig(phi_vuln=0.5, aggregate_floor=0.50)

vulnerable = Jurisdiction(id="v", level=2, tau=0.10,
                          state=State(justice={d: 0.20 for d in DIMENSIONS}))
robust     = Jurisdiction(id="r", level=2, tau=0.10,
                          state=State(justice={d: 0.80 for d in DIMENSIONS}))

assert effective_tau(vulnerable, config) == 0.05   # 0.5 * 0.10
assert effective_tau(robust, config) == 0.10
assert check_c3([vulnerable, robust], config) == ["v"]
```

**Notes.** C3 is not a violation check. It is a **threshold reduction**. The paper's §3.6.3 states this; the library reflects it. Use `effective_tau` inside C1 to apply the reduction.

### 8.4 `check_c4` — vertical alignment

**Signature.**

```python
def check_c4(
    jurisdictions: List[Jurisdiction],
    config: GSMConfig,
) -> List[Tuple[str, str, float]]:
```

Returns `(child_id, dimension, shortfall)` where `shortfall = (parent − phi_d) − child > 0`.

**Example.**

```python
from gsm_governance import GSMConfig, Jurisdiction, State, check_c4, DIMENSIONS

config = GSMConfig(phi_d={d: 0.10 for d in DIMENSIONS})

parent = Jurisdiction(id="p", level=1,
                      state=State(justice={d: 0.80 for d in DIMENSIONS}))
child  = Jurisdiction(id="c", level=2,
                      state=State(justice={d: 0.65 for d in DIMENSIONS}))
parent.add_child(child)

# Margin = 0.80 - 0.10 = 0.70. Child at 0.65 → shortfall 0.05.
violations = check_c4([parent, child], config)
assert len(violations) == 5
assert all(v[0] == "c" for v in violations)
assert all(abs(v[2] - 0.05) < 1e-9 for v in violations)
```

**Notes.** C4 is **absolute**, not proportional. A child may fall below a parent by at most `phi_d[d]`, regardless of the parent's absolute level. If you want proportional alignment, override the check; do not assume the library does what a proportional rule would do.

### 8.5 `check_all`

**Signature.**

```python
def check_all(
    jurisdictions: List[Jurisdiction],
    exploitation: Dict[Tuple[str, str], float],
    compensation: Dict[Tuple[str, str], CompensationVector],
    config: GSMConfig,
) -> dict:
```

Returns `{"c1": [...], "c2": [...], "c3": [...], "c4": [...]}`. The C1 result uses the delivered `check_c1`, not the corrected version. If you need the corrected version, call `check_c1_corrected` (§8.1) alongside or in place of `check_all`.

---

## 9. `gsm_governance.compensation`

The six-channel compensation vector of §3.5, Table 7.

### 9.1 `CompensationVector`

**Signature.**

```python
@dataclass
class CompensationVector:
    fiscal:           float = 0.0
    infrastructural:  float = 0.0
    representational: float = 0.0
    regulatory:       float = 0.0
    future:           float = 0.0
    restitutional:    float = 0.0
```

**Methods.**

- `total()` — sum of all channels.
- `is_adequate(exploitation, config)` — `total() + epsilon >= exploitation`. Conservative: `lambda = 1`.
- `channel_coverage(dimension)` — `True` if any channel targets this dimension.

**Example.**

```python
from gsm_governance import CompensationVector, GSMConfig

c = CompensationVector(fiscal=0.10, representational=0.05)
assert abs(c.total() - 0.15) < 1e-9
assert c.is_adequate(0.15, GSMConfig())
assert c.is_adequate(0.20, GSMConfig()) == False  # 0.15 < 0.20
```

### 9.2 Channel-dimension map

| Channel | Targets |
|---|---|
| `fiscal` | distributive |
| `infrastructural` | distributive, corrective |
| `representational` | procedural, recognition |
| `regulatory` | procedural, recognition, intergenerational |
| `future` | intergenerational |
| `restitutional` | corrective |

**Notes.** §3.5 of the paper writes adequacy as `lambda_j · Comp >= E` for some `lambda_j` in `(0, 1]`. The library uses `lambda = 1`, the conservative reading. To model partial adequacy, override `is_adequate` or supply compensation magnitudes accordingly. Do not modify `lambda` inside the library without documenting the change.

---

## 10. `gsm_governance.welfare.WelfareEvaluator`

Dimension-specific prioritarian welfare. Two modes (§4.3).

### 10.1 Construction

```python
from gsm_governance import GSMConfig, WelfareEvaluator

evaluator = WelfareEvaluator(GSMConfig(welfare_mode="quadratic"))
```

### 10.2 `welfare`

**Signature.**

```python
def welfare(self, jurisdictions: List[Jurisdiction], mode: Optional[str] = None) -> dict:
```

Returns `{"total": ..., "base": ..., "exploitation_penalty": 0.0, "compensation_credit": 0.0}`. In `welfare` alone, the last two are always zero; use `welfare_enhanced` for the full form.

**Quadratic mode (default).**

```
W = Σ_l Σ_i Σ_d w_d · [ γ_d · J − δ_d · (1 − J)² ]
```

**Linear-floor mode.**

```
W = Σ_l Σ_i [ Σ_d w_d · γ_d · J − Σ_d w_d · δ_d · max(0, floor_d − J) ]
```

**Example.**

```python
from gsm_governance import (
    GSMConfig, Jurisdiction, State, WelfareEvaluator, DIMENSIONS,
)

config = GSMConfig(welfare_mode="quadratic")
evaluator = WelfareEvaluator(config)

j = Jurisdiction(id="j", level=1,
                 state=State(justice={d: 0.60 for d in DIMENSIONS}))
result = evaluator.welfare([j])
print(f"base welfare = {result['base']:.4f}")
```

### 10.3 `welfare_enhanced`

**Signature.**

```python
def welfare_enhanced(
    self,
    jurisdictions: List[Jurisdiction],
    exploitation: Dict[Tuple[str, str], float],
    compensation: Dict[Tuple[str, str], CompensationVector],
) -> dict:
```

`W* = W + exploitation_penalty + compensation_credit`, where `exploitation_penalty = -Σ E` and `compensation_credit = Σ total(Comp)`.

**Example.**

```python
from gsm_governance import CompensationVector

expl = {("p", "c"): 0.10}
comp = {("p", "c"): CompensationVector(fiscal=0.08)}
result = evaluator.welfare_enhanced([j], expl, comp)
print(f"total = {result['total']:.4f}")
print(f"  base = {result['base']:.4f}")
print(f"  explo = {result['exploitation_penalty']:.4f}")   # -0.10
print(f"  comp = {result['compensation_credit']:.4f}")      # +0.08
```

### 10.4 `is_prioritarian`

Returns `True` iff `delta_w[d] > gamma_w[d]` for every dimension. The default is **not** prioritarian.

```python
assert WelfareEvaluator(GSMConfig()).is_prioritarian() == False
config = GSMConfig(
    gamma_w={d: 0.20 for d in DIMENSIONS},
    delta_w={d: 1.00 for d in DIMENSIONS},
)
assert WelfareEvaluator(config).is_prioritarian() == True
```

---

## 11. `gsm_governance.accountability.Accountability`

Dimension-specific cross-level accountability (§3.7).

### 11.1 Usage

```python
from gsm_governance import GSMConfig, Accountability, load_stylized_nordic

config = GSMConfig()
juris = load_stylized_nordic()
acc = Accountability(config)
acc.initialize(juris)

# After updating justice state, update accountability:
acc.update(juris)

# Read accountability for a jurisdiction, per dimension:
print(acc.A["province"]["distributive"])
```

### 11.2 Formula

```
A^{d,l}(t+1) = A^{d,l}(t) + lambda^{pd} · (J^{d,l+1} − J^{d,l})
```

`lambda_pd` is dimension-specific. The gap is child minus parent. A child whose justice exceeds its parent gains accountability; a child that falls below loses it.

**Notes.** `Simulation.step()` calls `acc.update()` automatically. If you use `Accountability` directly, call `update` yourself after every state change or you will read stale values. The `A` attribute is a plain dict keyed by `jurisdiction_id` and then by dimension.

---

## 12. `gsm_governance.enforcement`

Multi-channel policy intervention with cost, horizon, and recovery (§4.1).

### 12.1 `Intervention`

**Signature.**

```python
@dataclass
class Intervention:
    jurisdiction_id: str
    start_t:         int
    channel:         str           # fiscal | infrastructural | representational | regulatory | future | restitutional
    magnitude:       float
    dimension_target: Optional[str] = None   # informational; not used by the dynamics
    authority:        Optional[str] = None   # informational
```

### 12.2 `PolicyInterventionEnforcer`

**Signature.**

```python
class PolicyInterventionEnforcer:
    def __init__(self, config: GSMConfig)
    def add(self, intervention: Intervention)
    def apply(self, t: int, jurisdictions: List[Jurisdiction])
    def predicted_frequency_ceiling(self) -> float
```

**Example.**

```python
from gsm_governance import (
    GSMConfig, PolicyInterventionEnforcer, Intervention, load_stylized_nordic,
)

config = GSMConfig(kappa_int=0.10, tau_int=5)
juris = load_stylized_nordic()
enf = PolicyInterventionEnforcer(config)

enf.add(Intervention(
    jurisdiction_id="province",
    start_t=2,
    channel="fiscal",
    magnitude=0.30,
    authority="national",
))

for t in range(15):
    enf.apply(t, juris)

print(f"predicted ceiling: {enf.predicted_frequency_ceiling():.1f} interventions/period")
```

### 12.3 Channel effects

Each channel produces effects on specific dimensions and specific capabilities, weighted by `omega_k[channel]`:

| Channel | Justice dimensions | Capabilities |
|---|---|---|
| `fiscal` | distributive (+0.5) | competence (+0.1) |
| `infrastructural` | distributive (+0.3), corrective (+0.2) | competence (+0.1), cohesion (+0.05) |
| `representational` | procedural (+0.3), recognition (+0.3) | accountability (+0.1), cohesion (+0.05) |
| `regulatory` | procedural (+0.1), recognition (+0.2), intergenerational (+0.2) | accountability (+0.1), learning (+0.05) |
| `future` | intergenerational (+0.5) | continuity (+0.1) |
| `restitutional` | corrective (+0.5) | cohesion (+0.1) |

### 12.4 Cost

Every active intervention depletes cohesion and continuity by `0.5 × kappa_int × magnitude` per period. This is the paper's §4.1 claim about multi-channel cost. After `tau_int` periods, the intervention stops and a recovery drain begins (recovery_rate × channel effect × magnitude, decaying by 0.5 each period).

**Notes.** The `magnitude` should be interpreted as the *fraction of the target dimension's gap* the intervention aims to close, not as an absolute justice increment. The channel's `+0.5` etc. multipliers are further scaled by `omega_k[channel]`, so a `fiscal` intervention of `magnitude=0.30` produces roughly `0.30 × 0.5 × 0.20 = 0.03` on distributive justice per period, plus or minus channel weighting. Use this to calibrate magnitudes to your context.

---

## 13. `gsm_governance.simulation.Simulation`

The end-to-end engine. Ties everything together.

### 13.1 Construction

**Signature.**

```python
class Simulation:
    def __init__(
        self,
        config: GSMConfig,
        jurisdictions: List[Jurisdiction],
        interaction: Optional[JusticeInteractionMatrix] = None,
    )
```

**Example.**

```python
from gsm_governance import GSMConfig, Simulation, JusticeInteractionMatrix, load_stylized_nordic

config = GSMConfig(seed=42)
juris = load_stylized_nordic()

# Default interaction matrix
sim = Simulation(config, juris)

# Custom interaction matrix
M = JusticeInteractionMatrix(symmetry="symmetric")
sim = Simulation(config, juris, interaction=M)
```

### 13.2 `step`

**Signature.**

```python
def step(self) -> dict:
```

Runs one period. Returns:

```python
{
    "t": int,
    "welfare": {"total": float, "base": float,
                "exploitation_penalty": float, "compensation_credit": float},
    "violations": {"c1": [...], "c2": [...], "c3": [...], "c4": [...]},
    "n_exploitations": int,
    "total_exploitation": float,
}
```

**What happens in a step.**

1. Record previous state (for exploitation estimate).
2. Apply active interventions via `enforcer.apply(self.t, ...)`.
3. Estimate exploitation from the change in parent-child gaps.
4. Run `justice_step` and update justice; clip.
5. Run `capability_step` and update capabilities; clip.
6. Update accountability.
7. Run constraint checks.
8. Compute enhanced welfare.
9. Append row to `history`; increment `t`; return row.

**Example.**

```python
row = sim.step()
print(f"t={row['t']}, welfare={row['welfare']['total']:.4f}")
```

### 13.3 `run`

**Signature.**

```python
def run(self, n_steps: int) -> List[dict]:
```

Runs `n_steps` periods and returns the appended rows.

**Example.**

```python
history = sim.run(30)
```

### 13.4 Attributes

After construction:

- `sim.config` — the `GSMConfig` in use
- `sim.jurisdictions` — the list of `Jurisdiction` objects (mutated in place by `step`)
- `sim.interaction` — the `JusticeInteractionMatrix`
- `sim.welfare` — the `WelfareEvaluator`
- `sim.accountability` — the `Accountability` instance
- `sim.enforcer` — the `PolicyInterventionEnforcer`
- `sim.history` — the list of rows, one per step
- `sim.t` — the current step index

### 13.5 The exploitation model

`_exploitation` is the library's illustrative mechanism for estimating cross-jurisdiction exploitation. It computes, for each parent-child pair, the sum over dimensions of `0.5 × min(gain_by_parent, loss_by_child)` when both are positive. **This is illustrative, not empirical.** Override it if your research question involves a specific mechanism (see the tutorial's `EnvironmentalExternality` example).

---

## 14. `gsm_governance.estimation`

Scaffolding, not a solver. Read §3.3.3 and Appendix D.7 of the paper before using.

### 14.1 `EstimationSpec`

**Signature.**

```python
@dataclass
class EstimationSpec:
    sign_priors:     Dict[Tuple[str, str], str]              # "+", "-", "+/-"
    component_mask:  Dict[Tuple[str, str], Tuple[bool, bool]] # (has_plus, has_minus)
    symmetry:        str  = "asymmetric"
    m_max:           float = 0.30
```

**Methods.**

- `is_committed(d, e)` — `True` if `(d, e)` in `component_mask`.
- `prior_components(d, e)` — returns `(m_plus_prior, m_minus_prior)`. `None` means "estimate this component"; `0.0` means "fixed at zero".
- `net_sign_prior(d, e)` — returns `"+"`, `"-"`, `"+/-"`, or `"+/-"` for uncommitted.

**Example.**

```python
from gsm_governance.estimation import EstimationSpec

spec = EstimationSpec()

spec.is_committed("intergenerational", "procedural")   # True (contested)
spec.is_committed("distributive", "recognition")        # False (uncommitted)

spec.prior_components("intergenerational", "procedural")   # (None, None) — estimate both
spec.prior_components("procedural", "recognition")          # (None, 0.0) — estimate synergy, tension fixed at 0
spec.prior_components("distributive", "recognition")        # (0.0, 0.0) — both fixed at 0
```

### 14.2 `estimate_MJ`

Raises `NotImplementedError`. This is intentional. §3.3.3 and Appendix D.7 of the paper state that component identification requires natural experiments or cross-context designs that a library cannot manufacture.

**What you can do.** Use `EstimationSpec` to record your priors and component mask. Supply your own observation model and inference in a downstream module. `EstimationSpec` gives you the shared data structures so your priors are comparable to other studies.

Do not attempt to publish `estimate_MJ` output as an estimate. There is none.

---

## 15. `gsm_governance.data`

Loaders for the illustrative stylized-Nordic demonstration (§6).

### 15.1 `load_stylized_nordic`

**Signature.**

```python
def load_stylized_nordic() -> List[Jurisdiction]:
```

Returns three jurisdictions in a parent-child chain (`national` → `province` → `municipality`) with illustrative profiles.

**Example.**

```python
from gsm_governance import load_stylized_nordic

juris = load_stylized_nordic()
assert len(juris) == 3
assert juris[0].parent is None
assert juris[1].parent is juris[0]
assert juris[2].parent is juris[1]
```

**What the profiles are.** High-capability democracy profiles with moderate recognition and intergenerational shortfalls, matching the paper's §6.1 description. They are pedagogical. They are not measurements of any country.

### 15.2 `load_stylized_nordic_raw`

Returns the raw profile dict, useful for inspection or comparison.

```python
from gsm_governance import load_stylized_nordic_raw

raw = load_stylized_nordic_raw()
print(raw[1]["distributive"])   # 0.78 (national)
```

### 15.3 `load_denmark_raw`

**Deprecated.** Emits `DeprecationWarning`. Use `load_stylized_nordic_raw` instead.

---

## 16. Cookbook

Short recipes for common tasks.

### 16.1 Compare two configs on the same seed

```python
from dataclasses import replace
from gsm_governance import GSMConfig, Simulation, load_stylized_nordic

def end_welfare(config):
    sim = Simulation(config, load_stylized_nordic())
    return sim.run(30)[-1]["welfare"]["total"]

baseline = GSMConfig(seed=42)
prioritarian = replace(baseline, delta_w={d: 1.00 for d in
                        ("distributive","procedural","recognition",
                         "corrective","intergenerational")})

print(f"baseline     = {end_welfare(baseline):.4f}")
print(f"prioritarian = {end_welfare(prioritarian):.4f}")
```

### 16.2 Diagnose which dimension fails worst

```python
from collections import Counter
from gsm_governance import GSMConfig, Simulation, load_stylized_nordic

sim = Simulation(GSMConfig(seed=42), load_stylized_nordic())
history = sim.run(20)

by_dim = Counter(d for (_, d, _) in history[-1]["violations"]["c2"])
for d, n in by_dim.most_common():
    print(f"{d:>18}: {n} shortfalls")
```

### 16.3 Test the effect of a policy intervention

```python
from gsm_governance import GSMConfig, Simulation, Intervention, load_stylized_nordic

def run(magnitude):
    sim = Simulation(GSMConfig(seed=42), load_stylized_nordic())
    if magnitude > 0:
        sim.enforcer.add(Intervention(
            jurisdiction_id="province", start_t=5,
            channel="representational", magnitude=magnitude,
        ))
    return sim.run(30)[-1]

for mag in (0.0, 0.1, 0.3):
    final = run(mag)
    print(f"magnitude={mag:.1f}  welfare={final['welfare']['total']:.4f}  "
          f"C2={len(final['violations']['c2'])}")
```

### 16.4 Override the exploitation model

```python
from gsm_governance import Simulation, DIMENSIONS

class ZeroExploitation(Simulation):
    """Turn off exploitation entirely; useful as a baseline."""
    def _exploitation(self, prev_justice, prev_cap):
        return {}
```

### 16.5 Save a run to JSON

```python
import json
from dataclasses import asdict
from gsm_governance import GSMConfig, Simulation, load_stylized_nordic

sim = Simulation(GSMConfig(seed=42), load_stylized_nordic())
sim.run(30)

payload = {
    "library_version": __import__("gsm_governance").__version__,
    "config": asdict(sim.config),
    "history": sim.history,
    "final_justice": {j.id: dict(j.state.justice) for j in sim.jurisdictions},
}
with open("run.json", "w") as f:
    json.dump(payload, f, indent=2, default=float)
```

### 16.6 Sweep a parameter grid

```python
import itertools
from dataclasses import replace
from gsm_governance import GSMConfig, Simulation, load_stylized_nordic

grid = {"phi_vuln": [0.0, 0.5, 1.0], "welfare_mode": ["quadratic", "linear_floor"]}
for phi, mode in itertools.product(grid["phi_vuln"], grid["welfare_mode"]):
    config = replace(GSMConfig(seed=42), phi_vuln=phi, welfare_mode=mode)
    sim = Simulation(config, load_stylized_nordic())
    final = sim.run(30)[-1]
    print(f"phi={phi}  mode={mode:>12}  W={final['welfare']['total']:.4f}")
```

---

## 17. Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `ValueError: weights must sum to 1` | Custom `weights` dict does not sum to 1 | Normalize or leave default |
| `ValueError: phi_d must be non-negative` | Negative margin | Use non-negative values |
| `KeyError: 'recognition'` | State missing dimension | Populate all five `DIMENSIONS` |
| `ValueError: m_plus[...] out of [0, m_max]` | Synergy coefficient negative or too large | Check component sign and `m_max` |
| `ValueError: net ... exceeds |m_max|` | Combined components too large | Reduce `m_plus` or `m_minus` |
| `NotImplementedError: estimate_MJ is a scaffold` | You called `estimate_MJ` | Expected; supply your own inference |
| `DeprecationWarning: load_denmark_raw` | Old API | Use `load_stylized_nordic_raw` |
| C1 fires when you expect vulnerability adjustment | `check_c1` uses raw `tau` | Use `check_c1_corrected` (§8.1) |

**Import problems.** If `import gsm_governance` fails after `pip install -e .`, you likely have a stale `__pycache__`. Run `pip install -e . --force-reinstall --no-deps`. Confirm with `python -c "import gsm_governance; print(gsm_governance.__file__)"`.

**Version mismatch.** Check `gsm_governance.__version__` before relying on results. If it is not `0.4.0`, upgrade: `pip install -e . --upgrade`.

---

## 18. Performance

The library is designed for small-N studies, not for large-scale grid search.

- A 30-step simulation on three jurisdictions runs in ~5 ms on stock Python.
- A 100-point parameter grid at 5 seeds each (500 sims) runs in ~3 s.
- Memory is dominated by `sim.history`, which stores one dict per step per jurisdiction; a 1000-step run uses under 1 MB.

If you need to sweep thousands of configurations, `history` will dominate memory. Pass `track_history=False` — currently unsupported, but easy to add — or call `sim.step()` in a loop and keep only the rows you need.

The library has no C extensions and no `numpy` dependency in the core. Do not expect vectorized performance.

---

## 19. Extending the library

Three extension points, in order of how often you will need them.

### 19.1 Subclassing `Simulation`

Override `_exploitation` (see §16.4) or `step` to change dynamics. This is the primary extension point for research projects. Document your override in your paper's methods section.

### 19.2 Subclassing `WelfareEvaluator`

Override `welfare` to change the welfare form. The library supports quadratic and linear-floor; a lexicographic welfare function (worst dimension first) is a common research extension. See the tutorial's `LexicographicWelfare` example.

### 19.3 Custom `Intervention` channels

The channel-to-effect mapping is in `enforcement._CHANNEL_JUSTICE` and `_CHANNEL_CAPABILITY`. If you need a channel the library does not provide, subclass `PolicyInterventionEnforcer` and supply your own maps. Do not modify the library's constants.

**What not to extend.** Do not add fields to `GSMConfig` for parameters that shape the result but are not normative. If a parameter affects the output, it is normative and belongs in `GSMConfig`. If it is purely numerical (tolerances, iteration limits), put it in your subclass. The reporting discipline of §7.2 of the paper depends on this distinction.

---

## 20. API index

**`gsm_governance` (top-level exports).**

```
GSMConfig, DIMENSIONS, CAPABILITIES
CONTESTED_PAIRS, SINGLE_COMPONENT_TENSION_PAIRS, SINGLE_COMPONENT_SYNERGY_PAIRS
State, Jurisdiction
JusticeInteractionMatrix
justice_step, capability_step
check_c1, check_c2, check_c3, check_c4, check_all
WelfareEvaluator
Accountability
CompensationVector
PolicyInterventionEnforcer, Intervention
Simulation
load_stylized_nordic, load_stylized_nordic_raw
```

**Module-by-module.**

| Module | Public names |
|---|---|
| `gsm_governance.config` | `GSMConfig`, `DIMENSIONS`, `CAPABILITIES`, `CONTESTED_PAIRS`, `SINGLE_COMPONENT_TENSION_PAIRS`, `SINGLE_COMPONENT_SYNERGY_PAIRS` |
| `gsm_governance.entities` | `State`, `Jurisdiction` |
| `gsm_governance.justice` | `JusticeInteractionMatrix` |
| `gsm_governance.dynamics` | `justice_step`, `capability_step` |
| `gsm_governance.constraints` | `check_c1`, `check_c2`, `check_c3`, `check_c4`, `check_all`, `effective_tau` |
| `gsm_governance.compensation` | `CompensationVector` |
| `gsm_governance.welfare` | `WelfareEvaluator` |
| `gsm_governance.accountability` | `Accountability` |
| `gsm_governance.enforcement` | `PolicyInterventionEnforcer`, `Intervention` |
| `gsm_governance.simulation` | `Simulation` |
| `gsm_governance.estimation` | `EstimationSpec`, `estimate_MJ`, `DEFAULT_SIGN_PRIORS`, `DEFAULT_COMPONENT_MASK` |
| `gsm_governance.data` | `load_stylized_nordic`, `load_stylized_nordic_raw`, `load_denmark_raw` (deprecated) |

**Paper section-to-module map.**

| Paper section | Module |
|---|---|
| §3.1 Levels | `entities` |
| §3.2 State vector | `entities` |
| §3.3.1 Aggregation | `welfare`, `entities` |
| §3.3.2 Interaction matrix | `justice` |
| §3.3.3 Estimation | `estimation` |
| §3.3.4 Recognition | `constraints` (operationalization) |
| §3.4 Exploitation | `simulation`, `constraints` |
| §3.5 Compensation | `compensation` |
| §3.6 Constraints | `constraints` |
| §3.7 Accountability | `accountability` |
| §4.1 Dynamics | `dynamics`, `enforcement` |
| §4.2 Coupling | `dynamics` |
| §4.3 Welfare | `welfare` |
| §6 Stylized demonstration | `data`, `examples/stylized_nordic.py` |
| §7.2 Normative commitments | `config` |

---

## 21. What the library is not

A short section, because the boundary matters for research use.

**Not an estimator.** `estimate_MJ` is a scaffold. The empirical roadmap of §6.3 of the paper — a four-level calibration on federations with strong subnational statistics — is not implemented. If your study requires calibration, you will build it.

**Not a demo of the paper's claims.** The stylized-Nordic profiles are illustrative. The library does not test the paper's hypotheses; it provides the machinery so that *you* can. If you want to test H3 (non-exploitation → higher long-run flourishing), you must design the study, supply the data, and run the comparison.

**Not a policy tool.** The library can generate scenarios. It cannot generate recommendations. The constraints enforce the paper's four normative commitments; the welfare function evaluates them; the design of which scenario is best for which purpose is a normative judgment that the library does not make.

**Not finished.** §19 lists three extension points; §14 explains the estimation gap; §8.1 flags the C1 correction. These are honest frontiers, not defects. The library is at v0.4.0 because the theory is at v5; further development is expected to track the theory, not outrun it.

---

## 22. Getting help

- **Issues**: https://github.com/hongxueharriswang/gsm-governance/issues
- **Discussions**: for questions about how to model a specific mechanism, use Discussions rather than Issues.
- **The paper**: for questions about *why* the library is designed this way, the paper's sections are the reference. The section-to-module map in §20 is the index.
- **The tutorial**: for research workflows, `TUTORIAL.md`.
- **The README**: for installation, migration, and a summary of what changed in 0.4.0, `README.md`.

If you find a bug, report the version (`gsm_governance.__version__`), the config (`dataclasses.asdict`), and the smallest reproduction you can manage. The test suite is small enough that a well-formed bug report usually turns into a new test.