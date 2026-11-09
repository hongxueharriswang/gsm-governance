# A Researcher's Tutorial for `gsm-governance`

**Using the reference implementation of the computational theory of justice-centered multi-level governance in empirical and theoretical research**

---

## Who this tutorial is for

This tutorial assumes you are a researcher — in governance, computational social science, systems theory, public policy, or constitutional design — who wants to use `gsm-governance` as a **research instrument** rather than as a demonstration. It assumes:

- You have read the theory paper or its abstract (§1.4 for the irreducible core, §3.3.2 for the interaction decomposition, §3.6 for the four constraints, §6.3 for the empirical roadmap).
- You are comfortable with Python and with the idea that every parameter in a conditional theory must be reported.
- You have a research question — about policy design, parameter sensitivity, or the interaction of justice dimensions — that the library can help you answer.

What this tutorial does **not** do: teach the theory from scratch (read the paper), teach Python, or promise that the library is a complete empirical estimator (it is not — §11 explains what is scaffolding and what is not).

The tutorial is organized around **research workflows**, not around modules. Each section is a task you might want to perform, with a worked example you can adapt.

---

## 1. Setup (5 minutes)

```bash
git clone https://github.com/hongxueharriswang/gsm-governance.git
cd gsm-governance
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
pytest
```

You should see thirteen tests pass. Then open the folder in VS Code:

```bash
code .
```

The repository ships with `.vscode/launch.json` — you can hit F5 to run the example, or Ctrl+Shift+P → "Python: Configure Tests" to enable the built-in test runner.

**Verify the install.**

```python
import gsm_governance
print(gsm_governance.__version__)  # 0.4.0
```

If you see anything other than `0.4.0`, you are working against a stale copy. The library is versioned to the paper: 0.4.0 implements v5 of the theory, 0.3.0 implements v3.

---

## 2. Orientation: the theory in code

Five objects correspond to the paper's core constructs. You will use all five in every study.

| Object | What it is | Paper section |
|---|---|---|
| `GSMConfig` | Every normative parameter as an explicit field | §7.2 |
| `Jurisdiction` + `State` | A jurisdiction at a level, with `capabilities` and `justice` | §3.1–3.3 |
| `JusticeInteractionMatrix` | `M_J = M_J⁺ + M_J⁻` with pair typing | §3.3.2 |
| `Simulation` | The dynamic engine: state → dynamics → constraints → welfare | §4 |
| `WelfareEvaluator` | Dimension-specific prioritarian welfare | §4.3 |

The library enforces one constraint on how you use it. **Every normative commitment must be visible in `GSMConfig`.** There are no hidden defaults that shape the result. If a parameter is not in `GSMConfig`, it does not affect the simulation. This is what makes the output publishable.

The three innovations the paper calls irreducible — the justice gap, the five-dimensional capability, the constraint architecture — are not "features" of the library. They are the reason the library exists. Everything else is machinery to make them precise.

---

## 3. Your first simulation

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

Output:

```
welfare       = 3.7521
C2 violations = 9
C4 violations = 12
```

Two things to notice.

**First, aggregate welfare improves while floors are violated.** This is the paper's §6.1 finding, reproduced. Under default parameters with the stylized-Nordic profiles, the aggregate rises because capabilities drift upward while recognition, corrective, and intergenerational dimensions remain below their floors. You can see the same thing by looking at `final['violations']['c2']` — nine shortfalls across the three jurisdictions.

**Second, C4 violations are systematic.** Twelve shortfalls — one per dimension per parent-child pair, at two levels. The province falls below the national level in every dimension by more than `phi_d`, and the municipality below the province. C4 is doing what C4 is supposed to do: it exposes alignment failures that C1 (non-exploitation) does not catch.

Now look at the same data as a time series:

```python
print(f"{'t':>3} {'welfare':>10} {'base':>10} {'expl':>8} "
      f"{'C1':>3} {'C2':>3} {'C3':>3} {'C4':>3}")
for row in history:
    v = row["violations"]
    print(f"{row['t']:>3} {row['welfare']['total']:>10.4f} "
          f"{row['welfare']['base']:>10.4f} "
          f"{row['welfare']['exploitation_penalty']:>8.4f} "
          f"{len(v['c1']):>3} {len(v['c2']):>3} "
          f"{len(v['c3']):>3} {len(v['c4']):>3}")
```

You will see welfare plateauing, C2 violations persisting, C1 occasionally firing (the illustrative exploitation model in `Simulation._exploitation` fires when a parent gains justice at a child's expense), and C3 reporting vulnerable jurisdiction ids. That's your baseline. Everything else in this tutorial is a controlled departure from it.

---

## 4. The researcher's layer

The library is deliberately low-level. It does not impose a study structure. Your first task in any research project is to write a **thin wrapper** that:

1. Holds your `GSMConfig`, jurisdictions, and interaction matrix.
2. Records every run — config, seed, history — so results are reproducible.
3. Provides a small set of diagnostics tailored to your research question.

Here is a minimal starting point. Adapt it.

```python
# my_study/wrapper.py
import json
from dataclasses import asdict
from pathlib import Path
from gsm_governance import GSMConfig, Simulation, load_stylized_nordic

class Study:
    """A reproducible wrapper around a single GSM-J study."""

    def __init__(self, name: str, config: GSMConfig, jurisdictions=None):
        self.name = name
        self.config = config
        self.jurisdictions = jurisdictions or load_stylized_nordic()
        self.runs = []

    def run(self, n_steps: int, label: str = "") -> dict:
        sim = Simulation(self.config, self.jurisdictions)
        history = sim.run(n_steps)
        record = {
            "label": label,
            "n_steps": n_steps,
            "history": history,
            "final_justice": {
                j.id: dict(j.state.justice) for j in self.jurisdictions
            },
            "final_capabilities": {
                j.id: dict(j.state.capabilities) for j in self.jurisdictions
            },
        }
        self.runs.append(record)
        return record

    def save(self, path: str):
        payload = {
            "study_name": self.name,
            "library_version": __import__("gsm_governance").__version__,
            "config": asdict(self.config),
            "runs": self.runs,
        }
        Path(path).write_text(json.dumps(payload, indent=2, default=float))
```

Now the four things a reviewer will ask for — config, seeds, history, final state — are recorded by construction. Do not skip this step. Reproducibility is the difference between a study and a demo.

Two specific practices matter.

**Always set a seed.** The illustrative exploitation model in `Simulation._exploitation` does not use randomness, but the estimation scaffold and any custom model you add will. Set the seed in `GSMConfig`.

**Always report the library version.** The paper's v5 and v3 are not interchangeable: C3 and C4 changed behaviour, and welfare changed form. A result from 0.3.0 is not the same result from 0.4.0. Record `gsm_governance.__version__` in every saved study.

---

## 5. Research workflow: constraint diagnostics

Most studies begin with a diagnostic pass — where does the system fail, in which dimension, at which level? The library's four constraint functions are designed to answer this.

```python
from gsm_governance import (
    GSMConfig, Simulation, load_stylized_nordic,
    check_c1, check_c2, check_c3, check_c4,
)

config = GSMConfig(seed=42)
juris = load_stylized_nordic()
sim = Simulation(config, juris)
sim.run(20)

exploitation = sim._exploitation(
    {j.id: dict(j.state.justice) for j in juris},
    {j.id: dict(j.state.capabilities) for j in juris},
)
compensation = {}  # no compensation in this baseline

print("C1 (non-exploitation violations):")
for pair in check_c1(juris, exploitation, compensation, config):
    print(f"  {pair[0]} → {pair[1]}: E={exploitation[pair]:.4f}")

print("\nC2 (floor shortfalls, by dimension):")
c2 = check_c2(juris, config)
from collections import Counter
by_dim = Counter(d for (_, d, _) in c2)
for d, n in by_dim.most_common():
    print(f"  {d:>18}: {n} shortfalls")

print("\nC3 (vulnerable jurisdictions):")
for jid in check_c3(juris, config):
    from gsm_governance.constraints import effective_tau
    j = next(x for x in juris if x.id == jid)
    print(f"  {jid}: τ={j.tau:.3f} → τ_vuln={effective_tau(j, config):.3f}")

print("\nC4 (vertical alignment shortfalls, by dimension):")
c4 = check_c4(juris, config)
by_dim4 = Counter(d for (_, d, _) in c4)
for d, n in by_dim4.most_common():
    print(f"  {d:>18}: {n} shortfalls")
```

This diagnostic is the standard first table in any paper using GSM-J. Report it in your methods section. The *pattern* of violations — which dimension, which level — is often the substantive finding, not just the setup.

---

## 6. Research workflow: policy intervention experiments

The paper's §4.1 models intervention as a costly, multi-channel operation. The `PolicyInterventionEnforcer` implements this: an intervention targets a jurisdiction, a channel, and a magnitude, and has effects that unfold over `tau_int` periods before recovery begins.

The natural study design is **baseline vs. treated**, with the same seed and the same initial state, differing only in whether the intervention fires.

```python
from gsm_governance import GSMConfig, Simulation, Intervention, load_stylized_nordic

def run_with_intervention(channel: str, magnitude: float, target: str,
                          start_t: int = 5, n_steps: int = 30) -> list:
    juris = load_stylized_nordic()
    sim = Simulation(GSMConfig(seed=42), juris)
    if magnitude > 0:
        sim.enforcer.add(Intervention(
            jurisdiction_id=target,
            start_t=start_t,
            channel=channel,
            magnitude=magnitude,
            authority="national",
        ))
    return sim.run(n_steps)

baseline = run_with_intervention("fiscal", 0.0, "province")
treated  = run_with_intervention("fiscal", 0.30, "province")

print(f"{'t':>3} {'baseline':>10} {'treated':>10} {'Δ':>8}")
for t in [0, 10, 20, 29]:
    b = baseline[t]["welfare"]["total"]
    x = treated[t]["welfare"]["total"]
    print(f"{t:>3} {b:>10.4f} {x:>10.4f} {x - b:>+8.4f}")
```

The interesting comparison is not the end-state gap; it's the **shape** of the gap. A fiscal intervention on the province should raise distributive justice in the province while also depleting cohesion and continuity through the multi-channel cost (`kappa_int`). The depletion will show up as a drag on later welfare, and possibly as a C4 violation when the province's other dimensions fall below the national level. This is the paper's §4.1 claim — that intervention has *costs* — made operational.

A more comparative design holds the target fixed and varies the channel:

```python
channels = ["fiscal", "infrastructural", "representational",
            "regulatory", "future", "restitutional"]

print(f"{'channel':>18} {'welfare_end':>12} {'C2_end':>8} {'C4_end':>8} "
      f"{'cohesion_end':>14}")
for ch in channels:
    juris = load_stylized_nordic()
    sim = Simulation(GSMConfig(seed=42), juris)
    sim.enforcer.add(Intervention(
        jurisdiction_id="province", start_t=5, channel=ch, magnitude=0.30,
    ))
    history = sim.run(30)
    final = history[-1]
    print(f"{ch:>18} {final['welfare']['total']:>12.4f} "
          f"{len(final['violations']['c2']):>8} "
          f"{len(final['violations']['c4']):>8} "
          f"{juris[1].state.capabilities['cohesion']:>14.3f}")
```

Each channel affects a different dimension mix (`enforcement.py` documents the mapping). A representational intervention targets procedural and recognition justice; a future-oriented transfer targets intergenerational. The output table tells you which channel produces the largest welfare gain at the cost of which capability depletion — a substantive finding in its own right, and one that varies with `omega_k` (the channel weights), which you should report alongside the results.

---

## 7. Research workflow: sensitivity analysis

Conditional normative status (§1.7) is not a rhetorical hedge. It has an empirical consequence: **your result is conditional on your parameterization, and a well-conducted study demonstrates the conditioning.** Sensitivity analysis is not optional.

The cleanest pattern is a parameter grid. `dataclasses.replace` on `GSMConfig` triggers validation, so invalid points fail loudly.

```python
import itertools
from dataclasses import replace
from gsm_governance import GSMConfig, Simulation, load_stylized_nordic

baseline = GSMConfig(seed=42)

grid = {
    "phi_vuln": [0.0, 0.25, 0.50, 0.75, 1.0],
    "welfare_mode": ["quadratic", "linear_floor"],
}

results = []
for phi_vuln, mode in itertools.product(grid["phi_vuln"], grid["welfare_mode"]):
    config = replace(baseline, phi_vuln=phi_vuln, welfare_mode=mode)
    juris = load_stylized_nordic()
    sim = Simulation(config, juris)
    history = sim.run(50)
    final = history[-1]
    results.append({
        "phi_vuln": phi_vuln,
        "welfare_mode": mode,
        "final_welfare": final["welfare"]["total"],
        "c1_violations": len(final["violations"]["c1"]),
        "c2_violations": len(final["violations"]["c2"]),
        "c4_violations": len(final["violations"]["c4"]),
    })

print(f"{'phi_vuln':>9} {'mode':>14} {'welfare':>10} {'C1':>3} {'C2':>3} {'C4':>3}")
for r in results:
    print(f"{r['phi_vuln']:>9.2f} {r['welfare_mode']:>14} "
          f"{r['final_welfare']:>10.4f} "
          f"{r['c1_violations']:>3} {r['c2_violations']:>3} "
          f"{r['c4_violations']:>3}")
```

A parameter grid is the minimal version. Two extensions matter for publication:

**Multi-dimensional grids.** Vary `phi_vuln`, `phi_d`, `welfare_mode`, and `m_max` together. Report the full grid, not just the extremes. Reviewers will ask what happens at intermediate values.

**Seed replication.** Run each point at multiple seeds and report the mean and variance of the outcome. The illustrative exploitation model is deterministic, but any custom model you write (see §8) may be stochastic. Report seed-to-seed variability even if it is zero — that is itself a finding.

A full sensitivity study looks like this:

```python
grid = {
    "phi_vuln": [0.0, 0.5, 1.0],
    "phi_d": [{d: 0.02 for d in ("distributive","procedural","recognition",
                                 "corrective","intergenerational")},
              {d: 0.10 for d in ("distributive","procedural","recognition",
                                 "corrective","intergenerational")}],
    "welfare_mode": ["quadratic", "linear_floor"],
}
seeds = [42, 43, 44, 45, 46]

# ... run each combination at each seed, aggregate, report
```

The reporting standard: a table with parameter values as columns, outcome statistics as rows, and seed variance where relevant. The paper's Appendix B is a checklist of what must be reported. Follow it.

---

## 8. Working with your own data and exploitation model

The library ships with two kinds of scaffolding that you will almost certainly replace:

1. `load_stylized_nordic()` returns **illustrative profiles**, not measurements of any country. If you have real data, use it.
2. `Simulation._exploitation` uses an **illustrative** parent-exploits-child model. If your research question involves a specific mechanism, override it.

### Supplying your own jurisdictions

```python
from gsm_governance import Jurisdiction, State, DIMENSIONS, CAPABILITIES

def my_jurisdictions():
    """Replace with your own indicator data."""
    national = Jurisdiction(
        id="my_national",
        level=1,
        state=State(
            capabilities={c: 0.82 for c in CAPABILITIES},  # from V-Dem, WJP, etc.
            justice={
                "distributive":     0.74,
                "procedural":       0.79,
                "recognition":      0.61,
                "corrective":       0.42,
                "intergenerational":0.51,
            },
        ),
        tau=0.05,
    )
    province = Jurisdiction(
        id="my_province",
        level=2,
        state=State(
            capabilities={c: 0.70 for c in CAPABILITIES},
            justice={
                "distributive":     0.68,
                "procedural":       0.72,
                "recognition":      0.55,
                "corrective":       0.38,
                "intergenerational":0.47,
            },
        ),
        tau=0.05,
    )
    national.add_child(province)
    return [national, province]
```

Two rules for using your own data. **Report the sources for each dimension**, following §6.3's guidance. Distributive is best served (OECD *How's Life?*, SDG); procedural and recognition by WJP and V-Dem; corrective has no dedicated cross-national index and will require construction; intergenerational by natural-capital and fiscal-sustainability indicators; attitudes by WVS. **Report interpretive judgments** when your source does not measure the dimension directly. The library's `State` is a scalar per dimension; mapping your indicators to it is a calibration choice, and it belongs in your methods.

### Overriding the exploitation model

The default `_exploitation` uses an illustrative "parent gains at child's expense" mechanism. For a paper that models a specific externality — environmental, fiscal, regulatory — subclass `Simulation`.

```python
from gsm_governance import Simulation, DIMENSIONS

class EnvironmentalExternality(Simulation):
    """Model an environmental externality as intergenerational exploitation.

    A parent jurisdiction whose intergenerational justice improves at a rate
    above the fair-share benchmark imposes a loss on its children in the
    intergenerational dimension.
    """

    FAIR_SHARE_RATE = 0.02   # benchmark improvement per period
    EXTERNALITY_COEF = 0.8   # fraction of excess transferred as exploitation

    def _exploitation(self, prev_justice, prev_cap):
        out = {}
        for j in self.jurisdictions:
            if j.parent is None:
                continue
            p = j.parent
            parent_rate = (p.state.justice["intergenerational"]
                           - prev_justice[p.id]["intergenerational"])
            excess = max(0.0, parent_rate - self.FAIR_SHARE_RATE)
            if excess > 0:
                out[(p.id, j.id)] = self.EXTERNALITY_COEF * excess
        return out
```

Use it exactly like `Simulation`:

```python
sim = EnvironmentalExternality(GSMConfig(seed=42), my_jurisdictions())
history = sim.run(30)
```

The subclass is where your **theoretical contribution** lives. The library's job is to give you a well-defined state space, constraint system, and welfare function so that your mechanism is comparable to others.

### Modeling compensation regimes

`Simulation` passes an empty compensation dict to `check_all` at every step. To model a compensation regime, override `step` and inject it:

```python
class CompensatingSimulation(Simulation):
    """Simulation with a fixed compensation regime applied at each step."""

    def __init__(self, config, jurisdictions, compensation_by_pair):
        super().__init__(config, jurisdictions)
        self.compensation_by_pair = compensation_by_pair
        self.compensation_history = []

    def step(self):
        prev_J = {j.id: dict(j.state.justice) for j in self.jurisdictions}
        prev_C = {j.id: dict(j.state.capabilities) for j in self.jurisdictions}
        exploitation = self._exploitation(prev_J, prev_C)

        # Build compensation for the pairs that exploited this step
        compensation = {
            pair: self.compensation_by_pair(pair, e)
            for pair, e in exploitation.items()
            if self.compensation_by_pair(pair, e) is not None
        }
        self.compensation_history.append(compensation)

        # Parent step recomputes exploitation — override the check to use ours
        row = super().step()
        # Re-run constraint checks with our compensation
        from gsm_governance import check_all
        row["violations"] = check_all(
            self.jurisdictions, exploitation, compensation, self.config)
        return row
```

Then supply a compensation provider:

```python
from gsm_governance import CompensationVector

def full_fiscal_compensation(pair, exploitation):
    return CompensationVector(fiscal=exploitation)

sim = CompensatingSimulation(
    GSMConfig(seed=42),
    load_stylized_nordic(),
    full_fiscal_compensation,
)
history = sim.run(30)
```

Compare against a no-compensation baseline to test the paper's hypothesis that compensation converts violations into admissible arrangements. The difference between the two runs is your effect size.

---

## 9. Known issues and patches

Two things in the delivered library need a correction before you use them in research. Both are documented here rather than hidden.

### Issue 1: C1 does not apply the vulnerability adjustment

**The bug.** `check_c1` uses `jurisdiction.tau` directly, not `effective_tau(jurisdiction, config)`. Per §3.6.3 of the paper, C1 must use the vulnerability-reduced threshold. As delivered, the library does not do this.

**The fix.** Override the check in your study layer:

```python
from gsm_governance.constraints import effective_tau

def check_c1_corrected(jurisdictions, exploitation, compensation, config):
    """C1 with the §3.6.3 vulnerability adjustment applied."""
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

Use `check_c1_corrected` in place of `check_c1` throughout your study. Report the substitution in your methods. The paper's claim about vulnerability-sensitive non-exploitation is not testable without it.

### Issue 2: the estimation scaffold does not estimate

**The gap.** `estimate_MJ` raises `NotImplementedError`. This is deliberate: §3.3.3 and Appendix D.7 of the paper state that component identification requires natural experiments or cross-context designs that a library cannot manufacture.

**What you can do.** `EstimationSpec` supplies the sign priors and component mask your own Bayesian implementation needs. If your research involves estimating `M_J` from data, you will:

1. Construct an `EstimationSpec` with your priors.
2. Write or supply an observation model (`EstimationSpec` does not assume one).
3. Implement inference against `JusticeInteractionMatrix`'s data structures.

The estimation module is a **coordination point**, not a solver. Do not expect it to estimate; expect it to keep your priors and mask comparable across studies.

### Issue 3: `Simulation` uses an illustrative exploitation model

**The caveat.** If your research question concerns exploitation, override `_exploitation` (§8). The default is illustrative; do not publish results from it without stating that it is not a calibration.

### Issue 4: `data` returns illustrative profiles

`load_stylized_nordic()` returns profiles from §6 that are pedagogical. If your paper uses real data, supply your own (§8). The library will not check whether you did.

---

## 10. Reporting for publication

The paper's Appendix B lists what must be reported. The library makes it possible to record all of it. A study record should include:

**Config.** Serialize with `dataclasses.asdict`. Include every field, even the ones you set to defaults — reviewers will want to see the defaults.

```python
import json
from dataclasses import asdict

def record_config(config, path):
    with open(path, "w") as f:
        json.dump(asdict(config), f, indent=2)
```

**Seeds.** Record the seed used for each run. If you ran a grid at multiple seeds, record the mapping from grid point to seed.

**History.** `sim.history` is a list of dicts, one per step. Serialize it.

```python
def record_run(sim, path):
    payload = {
        "library_version": __import__("gsm_governance").__version__,
        "config_seed": sim.config.seed,
        "history": sim.history,
        "final_justice": {j.id: dict(j.state.justice) for j in sim.jurisdictions},
        "final_capabilities": {j.id: dict(j.state.capabilities) for j in sim.jurisdictions},
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=float)
```

**Effective thresholds.** If you report C1 violations, report the effective threshold per jurisdiction, not the raw `tau`:

```python
from gsm_governance.constraints import effective_tau
thresholds = {j.id: effective_tau(j, config) for j in sim.jurisdictions}
```

**Any overrides.** If you used `check_c1_corrected`, report that. If you subclassed `Simulation`, report the mechanism in the paper's methods section.

**Sensitivity results.** The full grid, not just the extremes. If a grid point produced non-monotonic results, say so.

**Version.** The library version. `0.3.0` and `0.4.0` produce different results from the same config because C3 and C4 changed behaviour. A reviewer reproducing your study needs the version.

---

## 11. Extending the library

Most research projects will need one of three extensions.

### A new constraint

If your research question involves a constraint the paper does not specify — say, a procedural-justice floor that scales with vulnerability — add it as a function in your study layer, not in the library. The library's contract is to implement the paper's constraints faithfully; your extensions belong in your paper's methods.

### A new capability coupling

`capability_step` implements a first-order drift toward mean justice, modulated by intervention deltas. If your research question requires a substantive coupling (e.g., competence → distributive justice with a lag), override `capability_step` in a subclass:

```python
from gsm_governance import Simulation
from gsm_governance.dynamics import capability_step

class LaggedCouplingSimulation(Simulation):
    def step(self):
        # Precompute the coupling deltas from the previous state
        deltas = {
            j.id: {"competence": 0.05 * j.state.justice["distributive"]}
            for j in self.jurisdictions
        }
        for j in self.jurisdictions:
            dC = capability_step(j, self.config, deltas=deltas[j.id])
            for c, dv in dC.items():
                j.state.capabilities[c] += dv
            j.state.clip()
        # Call super().step() with the capabilities already updated
        return super().step()
```

Document the override. The paper's §4.2 commits to co-evolution as a *theoretical* property; the specific form is not fixed, and your paper should state the form you used.

### A new welfare form

`WelfareEvaluator` supports two modes. A third — say, lexicographic on the worst-off dimension — would need a subclass:

```python
from gsm_governance import WelfareEvaluator, DIMENSIONS

class LexicographicWelfare(WelfareEvaluator):
    def welfare(self, jurisdictions, mode=None):
        # Rank dimensions by the worst-off jurisdiction's value
        worst = {d: min(j.state.justice[d] for j in jurisdictions)
                 for d in DIMENSIONS}
        # Order dimensions from worst-off to best-off
        ordered = sorted(DIMENSIONS, key=lambda d: worst[d])
        # Return a vector that supports lexicographic comparison
        return {
            "total": sum(worst[d] for d in ordered),  # placeholder
            "base": sum(worst[d] for d in ordered),
            "exploitation_penalty": 0.0,
            "compensation_credit": 0.0,
            "lexicographic_order": ordered,
            "worst_off_by_dimension": worst,
        }
```

The library's design allows this without modifying it. That is the point of keeping normative commitments in `GSMConfig` and the machinery in modules: you can change either without fighting the other.

---

## 12. Reference

**Config fields.**

| Field | Type | Paper section |
|---|---|---|
| `alpha`, `beta`, `gamma` | `dict[str, float]` | §4.1 |
| `gamma_w`, `delta_w`, `weights` | `dict[str, float]` | §4.3 |
| `welfare_mode` | `"quadratic"` or `"linear_floor"` | §4.3 |
| `floors`, `aggregate_floor`, `default_tau` | dict, float, float | §3.6 |
| `phi_vuln`, `phi_d`, `lambda_pd` | float, dict, dict | §3.6, §3.7 |
| `m_max`, `symmetry` | float, `"symmetric"/"asymmetric"` | §3.3.2–3.3.3 |
| `kappa_int`, `tau_int`, `omega_k`, `recovery_rate` | float, int, dict, float | §4.1 |
| `epsilon`, `seed` | float, int | — |

**Public functions.**

| Function | Returns | Paper section |
|---|---|---|
| `check_c1(jurisdictions, exploitation, compensation, config)` | `list[tuple[str, str]]` — see §9 Issue 1 | §3.6.1 |
| `check_c2(jurisdictions, config)` | `list[tuple[str, str, float]]` | §3.6.2 |
| `check_c3(jurisdictions, config)` | `list[str]` (vulnerable ids) | §3.6.3 |
| `check_c4(jurisdictions, config)` | `list[tuple[str, str, float]]` | §3.6.4 |
| `effective_tau(jurisdiction, config)` | `float` | §3.6.3 |
| `check_all(jurisdictions, exploitation, compensation, config)` | `dict` with `c1`–`c4` keys | §3.6 |
| `justice_step`, `capability_step` | `dict[str, float]` | §4.1, §4.2 |
| `WelfareEvaluator(config).welfare(jurisdictions, mode)` | `dict` | §4.3 |

**Module map** (for navigation):

- `config` — `GSMConfig`, `DIMENSIONS`, `CAPABILITIES`, pair constants
- `entities` — `State`, `Jurisdiction`
- `justice` — `JusticeInteractionMatrix` with `m_plus`, `m_minus`, `pair_type()`, `coupling()`
- `dynamics` — `justice_step`, `capability_step`
- `constraints` — C1–C4, `effective_tau`
- `compensation` — `CompensationVector` with `.is_adequate()`
- `welfare` — `WelfareEvaluator` with quadratic and linear modes
- `accountability` — `Accountability` with `A` dict
- `enforcement` — `PolicyInterventionEnforcer`, `Intervention`
- `simulation` — `Simulation` with `.step()`, `.run(n)`, `.history`
- `estimation` — `EstimationSpec`, `estimate_MJ` (scaffold, see §9)
- `data` — `load_stylized_nordic`, `load_stylized_nordic_raw`

---

## 13. Further reading

**The theory.** Read the paper before running substantive studies. §1.4 for the irreducible core, §2.4 for the ontological status of justice, §3.3.2 for the interaction decomposition, §3.6 for the constraints, §4.3 for the welfare function, §7.5 for the middle-range positioning. The library implements v5; the paper's section numbers are the map.

**What the library does not do.** §9 above, and the docstrings of `estimate_MJ` and `load_stylized_nordic`. The honest frontier of the library is the honest frontier of the empirical roadmap in §6.3 of the paper. Do not present the illustrative profiles as measurements, and do not present the illustrative exploitation model as a calibration.

**The next deliverable.** A model constitutional instrument derived from the same theory is in preparation as a separate document. It translates C1–C4, the pair typing, and the parameterization into enforceable constitutional language. Researchers working on constitutional design should expect it to matter for their work; it is not part of this library.

**Reporting standards.** Follow the paper's Appendix B. Every normative parameter is in `GSMConfig`; report them all. The three innovations the paper calls irreducible are testable — H3, H6, and H8 are the paper's own proposals for how to test them. Design your study to answer one of them, not to reproduce the demonstration.

---

## A closing note on what "research" means here

The library is not a study. It is an instrument. The paper's central claim — that justice-centered governance can be modeled precisely enough to be tested — is a claim about what is *possible*, not about what has been *done*. A research project using this library will:

1. Pose a specific question the paper's hypotheses do not answer (e.g., what happens to C4 violations under a specific federal reform?).
2. Parameterize the theory to match the institutional context.
3. Run the study, record the results, and report the parameterization and sensitivity.
4. State what the study cannot conclude — the empirical frontier (no estimation, illustrative profiles, the illustrative exploitation model).

That last step is the one most likely to be skipped and most likely to be caught by a reviewer. Do not skip it. The library was built with an explicit honesty about what it does not do; your paper should be too.